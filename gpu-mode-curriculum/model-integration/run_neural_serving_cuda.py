#!/usr/bin/env python3
"""Bounded CUDA autoregressive serving experiment.

This is an application-level promotion of the real neural KV-cache backend,
not the deterministic transport exercise.  It keeps CPU and CUDA outputs
separate, measures steady-state decode with CUDA events, and verifies the
loopback HTTP response against the CPU oracle.
"""

from __future__ import annotations

import json
import math
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

import torch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERVING_DIR = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING_DIR))
sys.path.insert(0, str(ROOT / "gpu-kernels-serving-lab"))
import server  # noqa: E402
from neural_generator import NeuralGenerator  # noqa: E402
from common.provenance import source_provenance  # noqa: E402


OUT = HERE / "reports" / "neural-serving-cuda.json"
PROMPTS = ["hello gpu", "attention cache", "decode step", "memory traffic"]
MAX_TOKENS = 8


def main() -> int:
    report = {
        "project": "model-integration",
        "experiment": "neural-serving-cuda",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gpu_execution_accepted": False,
        "measured": False,
        "model_trained": False,
    }
    if not torch.cuda.is_available():
        report.update({"status": "unavailable:cuda-runtime", "reason": "CUDA is not available"})
    else:
        cpu = NeuralGenerator("cpu")
        gpu = NeuralGenerator("cuda")
        expected = {prompt: cpu.complete(prompt, MAX_TOKENS)["text"] for prompt in PROMPTS}
        # Exclude first-use CUDA module/cache setup from event samples.
        gpu.generate(PROMPTS[0], MAX_TOKENS)
        torch.cuda.synchronize()
        decode_samples_ms = []
        direct_rows = []
        for prompt in PROMPTS:
            samples = []
            for _ in range(7):
                start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
                start.record()
                generated, _ = gpu.generate(prompt, MAX_TOKENS)
                end.record()
                end.synchronize()
                samples.append(float(start.elapsed_time(end)))
            text = "".join(gpu.model.alphabet[i] for i in generated)
            decode_samples_ms.extend(samples)
            direct_rows.append({
                "prompt": prompt,
                "text_matches_cpu": text == expected[prompt],
                "generated_tokens": len(generated),
                "median_decode_ms": median(samples),
                "samples_ms": samples,
            })

        previous = server.GENERATOR
        server.GENERATOR = gpu
        http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        worker = threading.Thread(target=http.serve_forever, daemon=True)
        worker.start()
        endpoint = f"http://127.0.0.1:{http.server_port}/v1/completions"
        http_rows = []
        batch_row = None
        try:
            for prompt in PROMPTS * 2:
                body = json.dumps({"prompt": prompt, "max_tokens": MAX_TOKENS}).encode()
                request = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
                started = time.perf_counter()
                with urllib.request.urlopen(request, timeout=30) as response:
                    payload = json.load(response)
                http_rows.append({
                    "prompt": prompt,
                    "request_seconds": time.perf_counter() - started,
                    "server_compute_ms": payload.get("server_compute_ms"),
                    "correct": payload.get("choices", [{}])[0].get("text") == expected[prompt],
                    "backend": payload.get("backend"),
                })
            batch_body = json.dumps({"prompts": PROMPTS, "max_tokens": MAX_TOKENS}).encode()
            batch_request = urllib.request.Request(
                endpoint.replace("/v1/completions", "/v1/batch_completions"),
                data=batch_body,
                headers={"Content-Type": "application/json"},
            )
            started = time.perf_counter()
            with urllib.request.urlopen(batch_request, timeout=30) as response:
                batch_payload = json.load(response)
            choices = batch_payload.get("choices", [])
            batch_row = {
                "prompt_count": len(PROMPTS),
                "request_seconds": time.perf_counter() - started,
                "server_compute_ms": batch_payload.get("server_compute_ms"),
                "completion_tokens": batch_payload.get("usage", {}).get("completion_tokens"),
                "prefix_tokens_reused": batch_payload.get("usage", {}).get("prefix_tokens_reused"),
                "correct": len(choices) == len(PROMPTS) and all(
                    choice.get("text") == expected[prompt]
                    for prompt, choice in zip(PROMPTS, choices)
                ),
                "backend": batch_payload.get("backend"),
            }
        finally:
            http.shutdown()
            http.server_close()
            worker.join(timeout=10)
            server.GENERATOR = previous
        passed = all(row["text_matches_cpu"] for row in direct_rows) and all(row["correct"] for row in http_rows) and bool(batch_row and batch_row["correct"])
        report.update({
            "status": "passed" if passed else "failed",
            "gpu_execution_accepted": passed,
            "measured": True,
            "device_name": torch.cuda.get_device_name(0),
            "torch_version": torch.__version__,
            "prompt_count": len(PROMPTS),
            "max_tokens": MAX_TOKENS,
            "direct_rows": direct_rows,
            "http_rows": http_rows,
            "batch_row": batch_row,
            "decode_median_ms": median(decode_samples_ms),
            "scope": "single-process loopback HTTP on one CUDA device with real autoregressive KV-cache decode; untrained model, closed-loop requests, no production capacity or language-quality claim",
        })
    report["provenance"] = source_provenance(ROOT, [Path(__file__), SERVING_DIR / "neural_generator.py", SERVING_DIR / "server.py"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2))
    return 0 if report["gpu_execution_accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
