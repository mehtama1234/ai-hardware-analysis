#!/usr/bin/env python3
"""Verify the measured CUDA speculative-decoding artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    rows = report.get("rows", [])
    checks = {
        "passed_gpu_report": report.get("status") == "passed" and report.get("gpu_execution_accepted") is True,
        "measured_cuda": report.get("measured") is True and report.get("device_name"),
        "scenario_count": len(rows) >= 5,
        "output_parity": all(row.get("output_parity") is True for row in rows),
        "adaptive_output_parity": all(row.get("adaptive_output_parity") is True for row in rows),
        "acceptance_accounted": all(0 <= row.get("accepted_tokens", -1) <= row.get("draft_tokens", -1) for row in rows),
        "rollback_accounted": all(row.get("rollback_tokens", -1) >= 0 and row.get("rollback_count", -1) >= 0 for row in rows),
        "kv_commit_accounted": all(row.get("kv_tokens_committed") == row.get("generated_tokens") for row in rows),
        "timings_present": all(row.get("baseline_ms", 0) > 0 and row.get("speculative_ms", 0) > 0 for row in rows),
        "adaptive_timings_present": all(row.get("adaptive_ms", 0) > 0 for row in rows),
        "low_acceptance_case": min((row.get("acceptance_rate", 1.0) for row in rows), default=1.0) < 0.95,
        "adaptive_fallback_observed": any(row.get("adaptive_policy_fallback") is True for row in rows),
        "calibrated_case_present": any(row.get("draft_kind") == "calibrated" for row in rows),
    }
    result = {"status": "passed" if all(checks.values()) else "failed", "checks": checks, "scenario_count": len(rows)}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
