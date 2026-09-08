#!/usr/bin/env python3
"""Compare uncached and KV-cached decode through the HTTP serving path."""

from __future__ import annotations

import hashlib
import json
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
ROOT = HERE.parent
REPO = ROOT if (ROOT / "gpu-kernels-serving-lab").exists() else ROOT.parent
SERVING = REPO / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
import server  # noqa: E402
from neural_generator import NeuralGenerator  # noqa: E402

REPORT = HERE / "reports" / "serving-bridge.json"
WORKLOADS = (
    {"id": "short-context", "prompt": "attention cache", "max_tokens": 12},
    {"id": "long-context", "prompt": "attention cache " * 5, "max_tokens": 24},
    {"id": "long-decode", "prompt": "attention cache", "max_tokens": 96},
)
CONCURRENCIES = (1, 2, 4)
REQUESTS_PER_LEVEL = 8
MODEL_HIDDEN = 128
MODEL_HEADS = 8


class DecodeModeGenerator:
    def __init__(self, mode: str, device: str):
        self.inner = NeuralGenerator(device, hidden=MODEL_HIDDEN, heads=MODEL_HEADS)
        self.mode = mode
        self.backend = f"neural-{mode}-decode"
        self.model_name = self.inner.model_name
        self._graph_lock = threading.Lock()

    def complete(self, prompt: str, max_tokens: int) -> dict:
        if self.mode == "cuda_graph":
            # A graph bundle owns static batch-1 addresses. Serialize requests
            # until a batched graph bucket exists; this makes the tradeoff
            # visible in the serving measurements instead of racing buffers.
            with self._graph_lock:
                generated, _ = self.inner.generate(prompt, max_tokens, cached=True, cache_storage="cuda_graph")
        else:
            generated, _ = self.inner.generate(
                prompt, max_tokens, cached=self.mode != "uncached",
                cache_storage="preallocated" if self.mode == "preallocated" else "dynamic",
            )
        return {
            "text": "".join(self.inner.model.alphabet[index] for index in generated),
            "generated_tokens": len(generated),
            "prompt_tokens": len(self.inner.encode(prompt)),
            "backend": self.backend,
        }


def _request(endpoint: str, prompt: str, max_tokens: int) -> dict:
    body = json.dumps({"prompt": prompt, "max_tokens": max_tokens}).encode()
    request = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return {"latency_ms": (time.perf_counter() - started) * 1000.0, "payload": payload}


def _run_mode(mode: str, device: str) -> dict:
    previous = server.GENERATOR, server.ADMISSION, server.MICRO_BATCH
    server.GENERATOR = DecodeModeGenerator(mode, device)
    server.ADMISSION = None
    server.MICRO_BATCH = None
    http = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    endpoint = f"http://127.0.0.1:{http.server_port}/v1/completions"
    rows = []
    try:
        for workload in WORKLOADS:
            prompt = workload["prompt"]
            max_tokens = workload["max_tokens"]
            expected = server.GENERATOR.complete(prompt, max_tokens)["text"]
            for concurrency in CONCURRENCIES:
                prompts = [prompt for _ in range(REQUESTS_PER_LEVEL)]
                started = time.perf_counter()
                with ThreadPoolExecutor(max_workers=concurrency) as pool:
                    results = list(pool.map(lambda item: _request(endpoint, item[0], item[1]), [(p, max_tokens) for p in prompts]))
                wave_ms = (time.perf_counter() - started) * 1000.0
                rows.append({
                    "workload": workload["id"],
                    "prompt_tokens": len(server.GENERATOR.inner.encode(prompt)),
                    "max_tokens": max_tokens,
                    "concurrency": concurrency,
                    "request_count": len(results),
                    "accepted": len(results),
                    "wave_elapsed_ms": wave_ms,
                    "latency_ms_samples": [row["latency_ms"] for row in results],
                    "latency_ms_median": float(statistics.median(row["latency_ms"] for row in results)),
                    "output_texts": [row["payload"]["choices"][0]["text"] for row in results],
                    "output_parity": all(row["payload"]["choices"][0]["text"] == server.GENERATOR.complete(prompts[index], max_tokens)["text"] for index, row in enumerate(results)),
                    "backend_labels": sorted({row["payload"].get("backend") for row in results}),
                    "expected_probe_nonempty": bool(expected),
                })
    finally:
        http.shutdown()
        http.server_close()
        thread.join(timeout=10)
        server.GENERATOR, server.ADMISSION, server.MICRO_BATCH = previous
    return {"mode": mode, "rows": rows}


def main() -> int:
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        uncached = _run_mode("uncached", device)
        cached = _run_mode("cached", device)
        preallocated = _run_mode("preallocated", device)
        cuda_graph = _run_mode("cuda_graph", device) if device == "cuda" else None
        checks = {
            "all_requests_completed": all(row["accepted"] == REQUESTS_PER_LEVEL for mode in (uncached, cached) for row in mode["rows"]),
            "all_outputs_nonempty": all(row["expected_probe_nonempty"] for mode in (uncached, cached) for row in mode["rows"]),
            "all_backend_labels_present": all(row["backend_labels"] for mode in (uncached, cached) for row in mode["rows"]),
            "concurrency_levels_present": [row["concurrency"] for row in cached["rows"]] == list(CONCURRENCIES) * len(WORKLOADS),
        }
        for left, right in zip(uncached["rows"], cached["rows"]):
            left_payloads = left["backend_labels"]
            right_payloads = right["backend_labels"]
            key = f"{left['workload']}_{left['concurrency']}"
            checks[f"backend_pair_{key}"] = bool(left_payloads and right_payloads)
            checks[f"cross_mode_output_parity_{key}"] = left["output_texts"] == right["output_texts"]
        for left, right in zip(uncached["rows"], preallocated["rows"]):
            key = f"{left['workload']}_{left['concurrency']}"
            checks[f"preallocated_backend_pair_{key}"] = bool(left["backend_labels"] and right["backend_labels"])
            checks[f"uncached_preallocated_output_parity_{key}"] = left["output_texts"] == right["output_texts"]
        if cuda_graph is not None:
            for left, right in zip(uncached["rows"], cuda_graph["rows"]):
                key = f"{left['workload']}_{left['concurrency']}"
                checks[f"cuda_graph_backend_pair_{key}"] = bool(left["backend_labels"] and right["backend_labels"])
                checks[f"uncached_cuda_graph_output_parity_{key}"] = left["output_texts"] == right["output_texts"]
        report = {
            "experiment": "batch1_decode_serving_bridge",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "passed" if all(checks.values()) else "failed",
            "evidence_kind": "measured_gpu" if device == "cuda" else "measured_cpu",
            "device": device,
            "gpu_execution_accepted": device == "cuda" and all(checks.values()),
            "protocol": {"workloads": list(WORKLOADS), "model_hidden": MODEL_HIDDEN, "model_heads": MODEL_HEADS, "concurrency_levels": list(CONCURRENCIES), "requests_per_level": REQUESTS_PER_LEVEL},
            "uncached": uncached,
            "cached": cached,
            "preallocated": preallocated,
            "cuda_graph": cuda_graph,
            "checks": checks,
            "timing_scope": "loopback HTTP request wall latency including server dispatch and autoregressive generation; excludes client queue wait outside the request",
            "limitations": ["untrained character model", "same-process loopback", "CPU result is not a GPU throughput claim", "no production capacity claim", "microbatching is a separate follow-up comparison"],
            "source_sha256": {str(path.relative_to(REPO)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__).resolve(), SERVING / "server.py", SERVING / "neural_generator.py", SERVING / "microbatch.py")},
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "evidence_kind": report["evidence_kind"], "device": device, "checks": checks}, indent=2))
        return 0 if report["status"] == "passed" else 1
    finally:
        torch.set_num_threads(previous_threads)


if __name__ == "__main__":
    raise SystemExit(main())
