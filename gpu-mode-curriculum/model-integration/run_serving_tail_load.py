#!/usr/bin/env python3
"""Repeated HTTP tail-load sweep for the opt-in microbatch server."""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
import server  # noqa: E402
from microbatch import MicroBatchScheduler  # noqa: E402
from neural_generator import NeuralGenerator  # noqa: E402

OUT = HERE / "reports" / "serving-tail-load-cpu.json"
CONCURRENCIES = (1, 2, 4, 8)
REQUESTS_PER_LEVEL = 16


def request(endpoint: str, index: int):
    body = json.dumps({"prompt": "hello", "max_tokens": 8}).encode()
    req = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            payload = json.load(response)
            return {"index": index, "status": response.status, "latency_ms": (time.perf_counter() - started) * 1000, "payload": payload}
    except urllib.error.HTTPError as error:
        return {"index": index, "status": error.code, "latency_ms": (time.perf_counter() - started) * 1000, "payload": json.loads(error.read().decode())}


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values); return ordered[min(len(ordered) - 1, max(0, int((len(ordered) - 1) * q)))]


def main():
    previous_threads = torch.get_num_threads(); torch.set_num_threads(1)
    previous = server.GENERATOR, server.ADMISSION, server.MICRO_BATCH
    generator = NeuralGenerator(); server.GENERATOR = generator; server.ADMISSION = None
    scheduler = MicroBatchScheduler(generator, max_batch=4, window_ms=2.0, max_pending=64); server.MICRO_BATCH = scheduler
    http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler); thread = threading.Thread(target=http.serve_forever, daemon=True); thread.start()
    endpoint = f"http://127.0.0.1:{http.server_port}/v1/completions"
    expected = generator.complete("hello", 8)["text"]
    rows = []
    try:
        for concurrency in CONCURRENCIES:
            started = time.perf_counter()
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                level = list(pool.map(lambda i: request(endpoint, i), range(REQUESTS_PER_LEVEL)))
            elapsed_ms = (time.perf_counter() - started) * 1000
            accepted = [row for row in level if row["status"] == 200]
            latencies = [row["latency_ms"] for row in accepted]
            rows.append({"concurrency": concurrency, "request_count": len(level), "accepted": len(accepted),
                         "rejected": len(level) - len(accepted), "wave_elapsed_ms": elapsed_ms,
                         "latency_ms": {"min": min(latencies), "p50": percentile(latencies, .50), "p95_nearest_rank": percentile(latencies, .95), "max": max(latencies)},
                         "output_parity": all(row["payload"].get("choices", [{}])[0].get("text") == expected for row in accepted),
                         "batch_modes": sorted({row["payload"].get("batch_mode") for row in accepted}),
                         "output_tokens_per_second": sum(row["payload"].get("choices", [{}])[0].get("text", "").__len__() for row in accepted) / max(elapsed_ms / 1000, 1e-9)})
    finally:
        http.shutdown(); http.server_close(); thread.join(timeout=10); snapshot = scheduler.snapshot(); scheduler.close(); server.GENERATOR, server.ADMISSION, server.MICRO_BATCH = previous; torch.set_num_threads(previous_threads)
    checks = {"all_levels_complete": all(row["accepted"] == REQUESTS_PER_LEVEL for row in rows),
              "parity_all_levels": all(row["output_parity"] for row in rows),
              "tail_metrics_present": all("p95_nearest_rank" in row["latency_ms"] for row in rows),
              "vectorized_observed": any("vectorized" in row["batch_modes"] for row in rows),
              "scheduler_accounted": snapshot["rejected_count"] == 0}
    report = {"experiment": "serving_tail_load_cpu", "generated_at": datetime.now(timezone.utc).isoformat(),
              "status": "passed" if all(checks.values()) else "failed", "measured": True, "gpu_execution_accepted": False,
              "concurrency_levels": list(CONCURRENCIES), "requests_per_level": REQUESTS_PER_LEVEL, "rows": rows,
              "scheduler": snapshot, "checks": checks,
              "scope": "same-process CPU loopback with 16 requests per concurrency and a 2-ms microbatch window; nearest-rank p95, synthetic untrained model, no production or GPU capacity claim",
              "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__).resolve(), SERVING / "server.py", SERVING / "microbatch.py", SERVING / "neural_generator.py")}}
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "checks": checks, "rows": rows}, indent=2)); return 0 if report["status"] == "passed" else 1


if __name__ == "__main__": raise SystemExit(main())
