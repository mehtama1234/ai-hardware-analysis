#!/usr/bin/env python3
"""Measured continuous-arrival microbatch scheduler contract."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
from microbatch import MicroBatchScheduler  # noqa: E402
from neural_generator import NeuralGenerator  # noqa: E402

OUT = HERE / "reports" / "serving-microbatch-cpu.json"


def main():
    import torch
    previous_threads = torch.get_num_threads(); torch.set_num_threads(1)
    generator = NeuralGenerator()
    scheduler = MicroBatchScheduler(generator, max_batch=3, window_ms=8.0)
    prompts = ["hello", "world", "there", "attention", "cache", "decode", "memory", "traffic"]
    started = time.perf_counter()
    try:
        with ThreadPoolExecutor(max_workers=len(prompts)) as pool:
            futures = [pool.submit(lambda prompt=prompt: scheduler.submit(prompt, 6).result()) for prompt in prompts]
            results = [future.result(timeout=20) for future in futures]
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        expected = [generator.complete(prompt, 6)["text"] for prompt in prompts]
    finally:
        snapshot = scheduler.snapshot(); scheduler.close(); torch.set_num_threads(previous_threads)
    checks = {
        "all_requests_completed": len(results) == len(prompts),
        "output_parity": [row["text"] for row in results] == expected,
        "batch_limit_respected": all(1 <= row["size"] <= 3 for row in snapshot["batches"]),
        "arrival_batches_observed": any(row["size"] > 1 for row in snapshot["batches"]),
        "vectorized_batches_observed": any(row["mode"] == "vectorized" for row in snapshot["batches"]),
        "batch_accounting": sum(row["size"] for row in snapshot["batches"]) == len(prompts),
    }
    report = {
        "experiment": "serving_microbatch_cpu", "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if all(checks.values()) else "failed", "measured": True,
        "gpu_execution_accepted": False, "max_batch": 3, "window_ms": 8.0,
        "request_count": len(prompts), "elapsed_ms": elapsed_ms, "checks": checks,
        "batches": snapshot["batches"],
        "scope": "same-process CPU arrival scheduler with bounded microbatch window; exact neural output parity; no HTTP admission, paged KV cache, GPU throughput or production tail claim",
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (Path(__file__).resolve(), SERVING / "microbatch.py", SERVING / "neural_generator.py")},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "checks": checks, "batches": snapshot["batches"]}, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
