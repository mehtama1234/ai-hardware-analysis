#!/usr/bin/env python3
"""Bounded queue, rejection, and cancellation probe for microbatch serving."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from queue import Full

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
from microbatch import MicroBatchScheduler  # noqa: E402

OUT = HERE / "reports" / "serving-backpressure-cpu.json"


class SlowGenerator:
    def encode(self, prompt):
        return list(prompt)

    def complete(self, prompt, max_tokens):
        time.sleep(0.04)
        return {"text": f"{prompt}:{max_tokens}"}

    def complete_batch(self, prompts, max_tokens):
        time.sleep(0.04)
        return {"choices": [{"text": f"{prompt}:{max_tokens}"} for prompt in prompts], "batch_mode": "vectorized"}


def main():
    # Keep the arrival window open while the first request is in flight.  This
    # makes cancellation of the queued request deterministic instead of racing
    # the worker's queue receive.
    scheduler = MicroBatchScheduler(SlowGenerator(), max_batch=1, window_ms=100.0, max_pending=3)
    accepted: list[tuple[str, Future]] = []; rejected = 0
    for index in range(12):
        try:
            future = scheduler.submit(f"request-{index}", 2)
            accepted.append((f"request-{index}", future))
        except Full:
            rejected += 1
    cancelled = accepted[-1][1] if accepted else None
    if cancelled is not None:
        cancelled.cancel()
    results = []
    for prompt, future in accepted:
        if future.cancelled():
            continue
        try:
            results.append((prompt, future.result(timeout=10)))
        except Exception as exc:
            results.append((prompt, {"error": repr(exc)}))
    snapshot = scheduler.snapshot(); scheduler.close()
    valid = all(row.get("text") == f"{prompt}:2" for prompt, row in results)
    checks = {
        "bounded_rejections": rejected >= 1 and snapshot["rejected_count"] == rejected,
        "cancellation_recorded": cancelled is None or snapshot["cancelled_count"] >= 1,
        "accepted_outputs_valid": valid,
        "queue_capacity_reported": snapshot["max_pending"] == 3,
        "accounting_consistent": len(results) + snapshot["cancelled_count"] + rejected == 12,
    }
    report = {"experiment": "serving_backpressure_cpu", "generated_at": datetime.now(timezone.utc).isoformat(),
              "status": "passed" if all(checks.values()) else "failed", "measured": True,
              "gpu_execution_accepted": False, "request_count": 12, "accepted_count": len(accepted),
              "rejected_count": rejected, "completed_count": len(results), "checks": checks,
              "scheduler": snapshot,
              "scope": "same-process CPU bounded queue with synthetic 40-ms backend; rejection/cancellation semantics, not production tail capacity or GPU serving",
              "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in (Path(__file__).resolve(), SERVING / "microbatch.py")}}
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "checks": checks, "scheduler": snapshot}, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
