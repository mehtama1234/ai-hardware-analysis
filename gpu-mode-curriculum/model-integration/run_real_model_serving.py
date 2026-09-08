#!/usr/bin/env python3
"""Measure a local trained causal LM through decode and HTTP serving.

No network access or model download is allowed: ``--model-path`` must point to
an already materialized Transformers checkpoint.  The report separates task
quality, decode timing, HTTP timing, and cancellation scope.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
import microbatch  # noqa: E402
import server  # noqa: E402
from real_model_serving import HuggingFaceGenerator  # noqa: E402


DEFAULT_MODEL = Path.home() / ".cache" / "huggingface" / "smolLM2-360M-Instruct"
OUT = HERE / "reports" / "real-model-serving-cpu.json"
QUALITY_CASES = (
    {"id": "arithmetic", "prompt": "What is 2 + 2? Answer with just the number.", "answers": ("4",)},
    {"id": "capital", "prompt": "What is the capital of France? Answer with one word.", "answers": ("paris",)},
    {"id": "gpu-concept", "prompt": "In GPU inference, what does batching combine? Answer briefly.", "answers": ("request", "requests", "inputs")},
    {"id": "python", "prompt": "What keyword defines a function in Python? Answer with one word.", "answers": ("def",)},
    {"id": "physics", "prompt": "What unit measures electrical resistance? Answer with one symbol or word.", "answers": ("ohm", "Ω")},
    {"id": "sorting", "prompt": "Which is smaller: 3 or 5? Answer with just the number.", "answers": ("3",)},
)
SERVING_PROMPTS = tuple(case["prompt"] for case in QUALITY_CASES[:3])


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _request(endpoint: str, prompt: str, max_tokens: int) -> dict:
    body = json.dumps({"prompt": prompt, "max_tokens": max_tokens}).encode()
    request = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = json.load(response)
    return {"latency_ms": (time.perf_counter() - started) * 1000.0, "payload": payload}


def _quality(generator: HuggingFaceGenerator, max_tokens: int) -> dict:
    rows = []
    for case in QUALITY_CASES:
        result = generator.complete(case["prompt"], max_tokens)
        normalized = result["text"].strip().lower()
        matched = any(answer.lower() in normalized for answer in case["answers"])
        rows.append({**case, "generated": result["text"], "matched": matched, "generated_tokens": result["generated_tokens"]})
    return {"cases": rows, "passed": sum(row["matched"] for row in rows), "total": len(rows),
            "accuracy": sum(row["matched"] for row in rows) / len(rows)}


def _decode_timing(generator: HuggingFaceGenerator, max_tokens: int, repeats: int) -> dict:
    prompt = SERVING_PROMPTS[0]
    for _ in range(2):
        generator.complete(prompt, max_tokens)
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        result = generator.complete(prompt, max_tokens)
        samples.append((time.perf_counter() - started) * 1000.0)
    return {"prompt": prompt, "max_tokens": max_tokens, "samples_ms": samples,
            "median_ms": statistics.median(samples), "output": result["text"]}


def _http_run(generator: HuggingFaceGenerator, *, use_microbatch: bool, max_tokens: int, concurrency: int) -> dict:
    previous = server.GENERATOR, server.MICRO_BATCH, server.REQUEST_TIMEOUT_SECONDS
    scheduler = None
    server.GENERATOR = generator
    server.MICRO_BATCH = None
    server.REQUEST_TIMEOUT_SECONDS = 180.0
    if use_microbatch:
        scheduler = microbatch.MicroBatchScheduler(generator, max_batch=4, window_ms=3.0, max_pending=16)
        server.MICRO_BATCH = scheduler
    http = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    endpoint = f"http://127.0.0.1:{http.server_port}/v1/completions"
    try:
        prompt = SERVING_PROMPTS[0]
        expected = generator.complete(prompt, max_tokens)["text"]
        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            results = list(pool.map(lambda _: _request(endpoint, prompt, max_tokens), range(concurrency)))
        wave_ms = (time.perf_counter() - started) * 1000.0
        outputs = [row["payload"]["choices"][0]["text"] for row in results]
        return {
            "mode": "microbatch" if use_microbatch else "direct",
            "concurrency": concurrency, "request_count": len(results), "wave_elapsed_ms": wave_ms,
            "latency_ms_samples": [row["latency_ms"] for row in results],
            "median_ms": statistics.median(row["latency_ms"] for row in results),
            "output_parity": all(output == expected for output in outputs),
            "backend_labels": sorted({row["payload"].get("backend") for row in results}),
            "scheduler": scheduler.snapshot() if scheduler is not None else None,
        }
    finally:
        http.shutdown(); http.server_close(); thread.join(timeout=10)
        if scheduler is not None:
            scheduler.close()
        server.GENERATOR, server.MICRO_BATCH, server.REQUEST_TIMEOUT_SECONDS = previous


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--max-tokens", type=int, default=8)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args(argv)
    if not args.model_path.is_dir():
        raise SystemExit(f"model path does not exist: {args.model_path}")
    torch.set_num_threads(2)
    report = {
        "experiment": "real_model_serving",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "failed", "measured": False, "gpu_execution_accepted": False,
        "model_path": str(args.model_path.resolve()), "requested_device": args.device,
        "local_files_only": True, "scope": "local cached SmolLM2-360M-Instruct checkpoint; real trained-model CPU quality and serving boundary; no production capacity or GPU claim",
    }
    if args.device == "cuda" and not torch.cuda.is_available():
        report.update(status="unavailable:cuda-runtime", reason="CUDA is not available")
    else:
        # Keep one model resident.  Loading a second 360M FP32 copy can force
        # a small host into swap and would measure memory pressure rather than
        # decode behavior.  The adapter's generation flag is safe to toggle
        # between serialized timing phases.
        generator = HuggingFaceGenerator(args.model_path, device=args.device, use_cache=True)
        quality = _quality(generator, args.max_tokens)
        cached_timing = _decode_timing(generator, args.max_tokens, args.repeats)
        generator.use_cache = False
        generator.backend = f"huggingface-{generator.model_name}-uncached"
        uncached_timing = _decode_timing(generator, args.max_tokens, args.repeats)
        generator.use_cache = True
        generator.backend = f"huggingface-{generator.model_name}-cached"
        direct = [_http_run(generator, use_microbatch=False, max_tokens=args.max_tokens, concurrency=level) for level in (1, 2)]
        batched = [_http_run(generator, use_microbatch=True, max_tokens=args.max_tokens, concurrency=level) for level in (1, 2, 4)]
        report.update({
            "status": "passed" if quality["accuracy"] >= 0.50 and all(row["output_parity"] for row in direct + batched) else "failed",
            "measured": True, "gpu_execution_accepted": args.device == "cuda",
            "device": str(generator.device), "device_name": torch.cuda.get_device_name(0) if generator.device.type == "cuda" else "cpu",
            "torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__,
            "model_name": generator.model_name, "model_parameters": sum(parameter.numel() for parameter in generator.model.parameters()),
            "quality": quality, "cached_decode": cached_timing, "uncached_decode": uncached_timing,
            "decode_speedup_cached_vs_uncached": uncached_timing["median_ms"] / max(cached_timing["median_ms"], 1e-9),
            "http_direct": direct, "http_microbatch": batched,
            "cancellation": {"mode": generator.cancellation_mode, "inflight_interruption_proven": False},
        })
    source_paths = [Path(__file__).resolve(), HERE / "real_model_serving.py", SERVING / "server.py", SERVING / "microbatch.py"]
    report["source_sha256"] = {str(path.relative_to(ROOT)): _sha256(path) for path in source_paths}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "measured": report["measured"], "quality": report.get("quality", {})}, indent=2))
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
