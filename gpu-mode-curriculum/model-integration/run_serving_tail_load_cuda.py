#!/usr/bin/env python3
"""CUDA microbatch tail-load sweep for the real neural serving backend.

This is deliberately a bounded single-device loopback experiment.  It measures
HTTP wall latency and CUDA-event compute time for the same request waves as the
CPU contract, while keeping production capacity and multi-GPU claims out of the
artifact.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import sys

import torch

HERE = Path(__file__).resolve().parent
# The local checkout keeps the serving lab beside ``gpu-mode-curriculum``;
# the Colab archive keeps the required serving lab inside the curriculum
# directory.  Resolve both layouts explicitly so the remote handoff exercises
# the same backend instead of silently falling back to an import failure.
LOCAL_ROOT = HERE.parents[1]
ARCHIVE_ROOT = HERE.parent
ROOT = LOCAL_ROOT if (LOCAL_ROOT / "gpu-kernels-serving-lab").is_dir() else ARCHIVE_ROOT
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
if not SERVING.is_dir():
    raise FileNotFoundError(f"serving backend not found at {SERVING}")
sys.path.insert(0, str(SERVING))
import server  # noqa: E402
from microbatch import MicroBatchScheduler  # noqa: E402
from neural_generator import NeuralGenerator  # noqa: E402
BATCH1 = ROOT / "gpu-mode-curriculum" / "batch1-decode-vertical-slice"
if not BATCH1.is_dir():
    BATCH1 = ROOT / "batch1-decode-vertical-slice"
sys.path.insert(0, str(BATCH1))
from run_serving_bridge import DecodeModeGenerator  # noqa: E402

OUT = HERE / "reports" / "serving-tail-load-cuda.json"
CONCURRENCIES = (1, 2, 4, 8)
REQUESTS_PER_LEVEL = 12
MAX_TOKENS = 8


def request(endpoint: str, index: int) -> dict:
    body = json.dumps({"prompt": "hello", "max_tokens": MAX_TOKENS}).encode()
    req = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.load(response)
            return {"index": index, "status": response.status,
                    "latency_ms": (time.perf_counter() - started) * 1000, "payload": payload}
    except urllib.error.HTTPError as error:
        return {"index": index, "status": error.code,
                "latency_ms": (time.perf_counter() - started) * 1000,
                "payload": json.loads(error.read().decode())}


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, int((len(ordered) - 1) * q)))]


def tail_report_contract(report: dict) -> bool:
    """Return whether a measured tail-load report has the required evidence."""
    if report.get("status") != "passed" or report.get("measured") is not True:
        return False
    levels = report.get("concurrency_levels", [])
    rows = report.get("rows", [])
    if not levels or [row.get("concurrency") for row in rows] != levels:
        return False
    if report.get("requests_per_level", 0) <= 0:
        return False
    for row in rows:
        latency = row.get("latency_ms", {})
        if row.get("accepted") != report["requests_per_level"]:
            return False
        if row.get("rejected") != 0 or row.get("output_parity") is not True:
            return False
        if not all(isinstance(latency.get(key), (int, float)) for key in ("p50", "p95_nearest_rank", "max")):
            return False
        if not isinstance(row.get("cuda_event_ms"), (int, float)) or row["cuda_event_ms"] < 0:
            return False
        if not row.get("backend_labels"):
            return False
    # Concurrency 1 may be a synthetic/contract fixture; for a multi-level
    # sweep require vectorized batching at one or more genuinely concurrent
    # levels, while a single-level contract must still show its declared mode.
    if max(levels) > 1:
        vectorized = any(
            any("vectorized" in mode for mode in row.get("batch_modes", []))
            for row in rows if row.get("concurrency", 1) > 1
        )
    else:
        vectorized = any(
            any("vectorized" in mode for mode in row.get("batch_modes", []))
            for row in rows
        )
    if not vectorized:
        return False
    scheduler = report.get("scheduler", {})
    return scheduler.get("rejected_count") == 0 and scheduler.get("cancelled_count") == 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=("microbatch", "cuda_graph_microbatch"),
        default="microbatch",
        help="decode backend exercised by the HTTP tail-load sweep",
    )
    args = parser.parse_args()
    report = {"experiment": "serving_tail_load_cuda",
              "generated_at": datetime.now(timezone.utc).isoformat(),
              "mode": args.mode,
              "status": "unavailable:cuda-runtime", "measured": False,
              "gpu_execution_accepted": False}
    if not torch.cuda.is_available():
        report["reason"] = "CUDA is not available"
    else:
        previous = server.GENERATOR, server.ADMISSION, server.MICRO_BATCH
        if args.mode == "cuda_graph_microbatch":
            generator = DecodeModeGenerator(args.mode, "cuda")
            generator.prepare([{"prompt": "hello", "max_tokens": MAX_TOKENS}])
        else:
            generator = NeuralGenerator("cuda")
        expected = generator.complete("hello", MAX_TOKENS)["text"]
        scheduler = MicroBatchScheduler(generator, max_batch=4, window_ms=2.0, max_pending=64)
        server.GENERATOR, server.ADMISSION, server.MICRO_BATCH = generator, None, scheduler
        http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        thread = threading.Thread(target=http.serve_forever, daemon=True)
        thread.start()
        endpoint = f"http://127.0.0.1:{http.server_port}/v1/completions"
        rows = []
        try:
            for concurrency in CONCURRENCIES:
                torch.cuda.synchronize()
                event_start = torch.cuda.Event(enable_timing=True)
                event_end = torch.cuda.Event(enable_timing=True)
                event_start.record()
                started = time.perf_counter()
                with ThreadPoolExecutor(max_workers=concurrency) as pool:
                    level = list(pool.map(lambda i: request(endpoint, i), range(REQUESTS_PER_LEVEL)))
                event_end.record()
                torch.cuda.synchronize()
                elapsed_ms = (time.perf_counter() - started) * 1000
                cuda_event_ms = event_start.elapsed_time(event_end)
                accepted = [row for row in level if row["status"] == 200]
                latencies = [row["latency_ms"] for row in accepted]
                rows.append({
                    "concurrency": concurrency, "request_count": len(level),
                    "accepted": len(accepted), "rejected": len(level) - len(accepted),
                    "wave_elapsed_ms": elapsed_ms,
                    "latency_ms": {"min": min(latencies), "p50": percentile(latencies, .50),
                                   "p95_nearest_rank": percentile(latencies, .95), "max": max(latencies)},
                    "cuda_event_ms": cuda_event_ms,
                    "output_parity": all(row["payload"].get("choices", [{}])[0].get("text") == expected for row in accepted),
                    "batch_modes": sorted({row["payload"].get("batch_mode") for row in accepted}),
                    "backend_labels": sorted({row["payload"].get("backend") for row in accepted}),
                    "output_tokens_per_second": (sum(len(row["payload"].get("choices", [{}])[0].get("text", "")) for row in accepted)
                                                  / max(elapsed_ms / 1000, 1e-9)),
                })
        finally:
            http.shutdown(); http.server_close(); thread.join(timeout=10)
            snapshot = scheduler.snapshot(); scheduler.close()
            server.GENERATOR, server.ADMISSION, server.MICRO_BATCH = previous
        checks = {
            "all_levels_complete": all(row["accepted"] == REQUESTS_PER_LEVEL for row in rows),
            "parity_all_levels": all(row["output_parity"] for row in rows),
            "tail_metrics_present": all("p95_nearest_rank" in row["latency_ms"] for row in rows),
            "cuda_event_samples_present": all(isinstance(row.get("cuda_event_ms"), (int, float)) for row in rows),
            "vectorized_observed": any("vectorized" in row["batch_modes"] for row in rows),
            "scheduler_accounted": snapshot["rejected_count"] == 0 and snapshot["cancelled_count"] == 0,
        }
        report.update({"status": "passed" if all(checks.values()) else "failed",
                       "measured": True, "gpu_execution_accepted": all(checks.values()),
                       "device_name": torch.cuda.get_device_name(0), "torch_version": torch.__version__,
                       "concurrency_levels": list(CONCURRENCIES), "requests_per_level": REQUESTS_PER_LEVEL,
                       "max_tokens": MAX_TOKENS, "rows": rows, "scheduler": snapshot,
                       "checks": checks,
                       "timing_scope": "wall latency is measured per HTTP request; cuda_event_ms is the synchronized default-stream event span for each request wave",
                       "scope": "single-process loopback HTTP on one CUDA device; 12 requests per concurrency and a 2-ms microbatch window; untrained model, no production capacity or multi-GPU claim"})
        report["checks"]["report_contract"] = tail_report_contract(report)
        report["gpu_execution_accepted"] = all(report["checks"].values())
        report["status"] = "passed" if report["gpu_execution_accepted"] else "failed"
    source_paths = [Path(__file__).resolve(), SERVING / "server.py", SERVING / "microbatch.py", SERVING / "neural_generator.py"]
    if args.mode == "cuda_graph_microbatch":
        source_paths.append(BATCH1 / "run_serving_bridge.py")
    report["source_sha256"] = {
        str(path.relative_to(ROOT.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source_paths
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2))
    return 0 if report["gpu_execution_accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
