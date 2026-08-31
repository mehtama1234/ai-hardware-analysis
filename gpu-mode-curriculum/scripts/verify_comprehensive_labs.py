#!/usr/bin/env python3
"""Verify the hand-written comprehensive GPUMODE lab code layer."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMPREHENSIVE = ROOT / "comprehensive-labs"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not (COMPREHENSIVE / "plan.json").exists():
        subprocess.run([sys.executable, "scripts/build_comprehensive_lab_plan.py"], cwd=ROOT, check=True)
    if not (COMPREHENSIVE / "run-report.json").exists():
        subprocess.run([sys.executable, "scripts/run_comprehensive_labs.py"], cwd=ROOT, check=True)
    plan = load_json(COMPREHENSIVE / "plan.json")
    report = load_json(COMPREHENSIVE / "run-report.json")
    require(plan["coverage"]["lesson_count"] == 118, "expected 118 GPUMODE lessons in comprehensive plan")
    require(plan["coverage"]["covered_lessons"] == 118, "comprehensive lab plan does not cover every lesson")
    require(not plan["coverage"]["uncovered_lessons"], "comprehensive lab plan has uncovered lessons")
    require(len(plan["labs"]) == 8, "expected eight comprehensive labs")
    require(report["lab_count"] == len(plan["labs"]), "run report lab count mismatch")
    require(report["failed"] == 0, "comprehensive lab run has failures")
    require(report["passed"] == len(plan["labs"]), "not every comprehensive lab passed")
    for lab in plan["labs"]:
        implementation = ROOT / lab["implementation"]
        measurement = COMPREHENSIVE / "measurements" / f"{lab['id']}.json"
        require(implementation.exists(), f"missing implementation {implementation}")
        require(lab["lesson_count"] > 0, f"{lab['id']} has no mapped lessons")
        require(measurement.exists(), f"missing measurement for {lab['id']}")
        artifact = load_json(measurement)
        require(artifact["status"] == "passed", f"{lab['id']} measurement did not pass")
        checks = artifact.get("measurement", {}).get("checks", [])
        require(len(checks) >= 4, f"{lab['id']} has too few checks")
        require(all(row.get("passed") for row in checks), f"{lab['id']} has failed checks")
    print(
        json.dumps(
            {
                "facts": {
                    "comprehensive_labs": len(plan["labs"]),
                    "covered_lessons": plan["coverage"]["covered_lessons"],
                    "passed_labs": report["passed"],
                    "failed_labs": report["failed"],
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPUMODE comprehensive lab verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
