#!/usr/bin/env python3
"""Verify a trained-model CUDA tail-load artifact without rerunning it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    profile = report.get("model_profile", {})
    rows = report.get("rows", [])
    checks = {
        "report_passed": report.get("status") == "passed",
        "gpu_accepted": report.get("gpu_execution_accepted") is True,
        "trained_model": profile.get("trained") is True,
        "quality_gate": profile.get("quality_passed") is True,
        "heldout_accuracy": profile.get("heldout_next_token_accuracy", 0) >= 0.85,
        "cached_tail_parity": all(row.get("output_parity") is True for row in rows),
        "p95_present": all("p95_nearest_rank" in row.get("latency_ms", {}) for row in rows),
        "cuda_events_present": all(isinstance(row.get("cuda_event_ms"), (int, float)) for row in rows),
        "vectorized_observed": any("vectorized" in mode for row in rows for mode in row.get("batch_modes", [])),
        "scheduler_clean": report.get("scheduler", {}).get("rejected_count") == 0 and report.get("scheduler", {}).get("cancelled_count") == 0,
    }
    result = {"status": "passed" if all(checks.values()) else "failed", "checks": checks, "concurrency_levels": report.get("concurrency_levels", [])}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
