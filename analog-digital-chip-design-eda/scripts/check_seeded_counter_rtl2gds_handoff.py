#!/usr/bin/env python3
"""Independently verify the seeded-counter RTL2GDS handoff."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff", type=Path)
    args = parser.parse_args()
    report = json.loads(args.handoff.read_text(encoding="utf-8"))
    errors = []
    if report.get("schema_version") != "seeded-counter-model-repair-rtl2gds-handoff-v1": errors.append("unexpected schema")
    if report.get("status") != "passed": errors.append("handoff is not passed")
    if report.get("model", {}).get("repair_match") is not True or report.get("model", {}).get("grounded") is not True: errors.append("model repair is not accepted")
    if report.get("repair_retest", {}).get("status") != "passed" or report.get("repair_retest", {}).get("model_generated") is not True or report.get("repair_retest", {}).get("original_unchanged") is not True: errors.append("repair retest is not safe and passed")
    if report.get("formal", {}).get("status") != "passed" or report.get("formal", {}).get("proof") != "proven": errors.append("formal proof is missing")
    if report.get("formal", {}).get("property_count", 0) < 3 or not all(item.get("passed") is True for item in report.get("formal", {}).get("property_runs", [])): errors.append("independent formal property suite is incomplete")
    physical = report.get("physical", {})
    if physical.get("flow_status") != "flow completed" or physical.get("source_match") is not True or physical.get("lvs_errors") != 0: errors.append("physical handoff is not clean")
    if physical.get("gds_present") is not True or physical.get("xor_report") is not True: errors.append("physical artifacts are missing")
    metrics = physical.get("metrics", {})
    if metrics.get("tritonRoute_violations") != "0" or metrics.get("Magic_violations") != "0": errors.append("physical DRC metrics are not clean")
    if any(metrics.get(key) is None for key in ("spef_wns", "spef_tns", "wns", "tns")): errors.append("extracted STA metrics are incomplete")
    if errors:
        for error in errors: print(f"ERROR: {error}")
        return 1
    print(json.dumps({"status": "passed", "design": report.get("design"), "lvs_errors": 0, "formal": "proven", "source_match": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
