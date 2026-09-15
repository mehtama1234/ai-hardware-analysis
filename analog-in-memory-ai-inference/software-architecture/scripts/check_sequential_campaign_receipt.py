#!/usr/bin/env python3
"""Evaluate a sequential or fixed-decision FS/FF campaign receipt."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_CODES = [0, 2, 4, 6, 7]


def evaluate_case(report: dict) -> dict:
    rows = report.get("conversions", [])
    decoded = [row.get("final_code") for row in rows]
    expected = [row.get("expected_code") for row in rows]
    coverage = bool(report.get("conversion_coverage_complete")) and len(rows) == len(EXPECTED_CODES)
    code_map = decoded == EXPECTED_CODES and expected == EXPECTED_CODES
    legal = bool(report.get("bottom_plate_in_legal_range")) and all(
        bool(row.get("bottom_plate_in_legal_range")) for row in rows
    )
    return {
        "status": "accepted" if coverage and code_map and legal else "rejected",
        "coverage_complete": coverage,
        "decoded_codes": decoded,
        "expected_codes": expected,
        "code_map_pass": code_map,
        "bottom_plate_legal": legal,
        "runner_status": report.get("status"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign_summary", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    summary = json.loads(args.campaign_summary.read_text(encoding="utf-8"))
    cases = {}
    for corner in ("fs", "ff"):
        case = summary.get("cases", {}).get(corner, {})
        report = case.get("report") or {}
        cases[corner] = evaluate_case(report) if report else {
            "status": "rejected",
            "coverage_complete": False,
            "decoded_codes": [],
            "expected_codes": [],
            "code_map_pass": False,
            "bottom_plate_legal": False,
            "runner_status": "missing_child_report",
        }
    result = {
        "result_type": "sequential_campaign_receipt_evaluation",
        "status": "accepted" if all(case["status"] == "accepted" for case in cases.values()) else "rejected",
        "cases": cases,
        "required_corners": ["fs", "ff"],
        "required_codes": EXPECTED_CODES,
        "claim_boundary": "Receipt evaluation only; a pass does not authorize mismatch, energy, extracted-layout, silicon, or workload claims.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "accepted" else 2


if __name__ == "__main__":
    raise SystemExit(main())
