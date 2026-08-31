#!/usr/bin/env python3
"""Verify GPU measurement acceptance and rejection logic."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gpu-measurement-queue"))

from gpu_measurement_queue.acceptance_logic import REPORT_JSON, REPORT_MD, build_acceptance_logic_report  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    report = build_acceptance_logic_report()
    cases: list[dict[str, Any]] = report.get("cases", [])
    require(report.get("status") == "passed", "GPU acceptance logic report failed")
    require(report.get("case_count") == len(cases) >= 9, "case count mismatch")
    require(report.get("accepted_good_cases") == len(cases), "not every good case was accepted")
    require(report.get("rejected_bad_cases") == len(cases), "not every bad case was rejected")
    for case in cases:
        require(case.get("good", {}).get("accepted") is True, f"{case.get('step_id')} good case rejected")
        require(case.get("bad", {}).get("accepted") is False, f"{case.get('step_id')} bad case accepted")
        require(case.get("good", {}).get("checks"), f"{case.get('step_id')} missing good checks")
        require(case.get("bad", {}).get("checks"), f"{case.get('step_id')} missing bad checks")
    require(REPORT_JSON.exists(), "acceptance logic JSON report missing")
    require(REPORT_MD.exists(), "acceptance logic markdown report missing")
    print(
        json.dumps(
            {
                "facts": {
                    "cases": report["case_count"],
                    "accepted_good": report["accepted_good_cases"],
                    "rejected_bad": report["rejected_bad_cases"],
                    "status": report["status"],
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE GPU acceptance logic verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
