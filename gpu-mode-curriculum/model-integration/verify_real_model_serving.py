#!/usr/bin/env python3
"""Verify the local real-model quality and serving evidence contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    quality = report.get("quality", {})
    rows = quality.get("cases", [])
    http_rows = report.get("http_direct", []) + report.get("http_microbatch", [])
    checks = {
        "passed_report": report.get("status") == "passed",
        "measured": report.get("measured") is True,
        "local_only": report.get("local_files_only") is True,
        "real_model": report.get("model_parameters", 0) >= 100_000_000,
        "quality_cases": len(rows) >= 6,
        "quality_threshold": quality.get("accuracy", 0.0) >= 0.50,
        "decode_timings": report.get("cached_decode", {}).get("median_ms", 0) > 0 and report.get("uncached_decode", {}).get("median_ms", 0) > 0,
        "http_rows": len(http_rows) >= 5,
        "http_parity": all(row.get("output_parity") is True for row in http_rows),
        "microbatch_observed": any(row.get("mode") == "microbatch" for row in http_rows),
        "cancellation_scoped": report.get("cancellation", {}).get("inflight_interruption_proven") is False,
    }
    result = {"status": "passed" if all(checks.values()) else "failed", "checks": checks, "report": str(args.report)}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

