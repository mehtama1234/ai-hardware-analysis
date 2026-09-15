#!/usr/bin/env python3
"""Run and validate the checked-in time-zero scheduling regression matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification_platform.scheduling import run_time_zero_regression


CASES = {
    "normal_completion": ("normal_completion.sv", "normal_completion", "passed"),
    "test_failure": ("test_failure.sv", "formal_or_test_failure", "blocked"),
    "premature_termination": ("premature_termination.sv", "premature_time_zero_termination", "blocked"),
    "missing_stimulus": ("missing_stimulus.sv", "missing_stimulus", "blocked"),
    "timeout_deadlock": ("timeout_deadlock.sv", "timeout_or_deadlock", "blocked"),
}


def run_matrix(output: str | Path, *, timeout_seconds: float = 1.0) -> dict[str, object]:
    output_path = Path(output)
    # Keep the matrix stable under CI load: the timeout is a runtime bound for
    # the fixture, not a sub-second process-startup benchmark.
    effective_timeout = max(timeout_seconds, 10.0)
    results: dict[str, object] = {}
    for name, (filename, expected_outcome, expected_status) in CASES.items():
        result = run_time_zero_regression(
            ROOT / "benchmarks" / "time_zero_regressions" / filename,
            run_root=output_path / name, source_revision="time-zero-matrix-v1",
            timeout_seconds=effective_timeout,
        )
        results[name] = {
            "status": result["status"], "outcome": result["outcome"],
            "expected_status": expected_status, "expected_outcome": expected_outcome,
            "passed_expectation": result["status"] == expected_status and result["outcome"] == expected_outcome,
            "result": result,
        }
    passed = all(item["passed_expectation"] for item in results.values())
    report: dict[str, object] = {
        "schema_version": "time-zero-regression-matrix-v1",
        "status": "passed" if passed else "blocked",
        "cases": results,
        "claim_boundary": "classification regression only; does not prove Verilator coroutine/UVM compatibility",
    }
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "matrix-result.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=1.0)
    args = parser.parse_args()
    report = run_matrix(args.output, timeout_seconds=args.timeout_seconds)
    print(json.dumps({"status": report["status"], "output": str(args.output), "cases": len(CASES)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
