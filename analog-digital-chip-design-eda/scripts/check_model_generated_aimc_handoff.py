#!/usr/bin/env python3
"""Independently verify the model-generated AIMC RTL2GDS handoff."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff", type=Path)
    args = parser.parse_args()
    handoff = json.loads(args.handoff.read_text(encoding="utf-8"))
    errors = []
    if handoff.get("schema_version") != "model-generated-aimc-rtl2gds-handoff-v1":
        errors.append("unexpected handoff schema")
    if handoff.get("status") != "passed":
        errors.append("handoff is not passed")
    if handoff.get("llm", {}).get("acceptance") != "passed":
        errors.append("LLM acceptance is not passed")
    if handoff.get("approved_retest", {}).get("status") != "passed":
        errors.append("approved retest is not passed")
    if handoff.get("approved_retest", {}).get("model_generated") is not True:
        errors.append("repair was not model-generated")
    physical = handoff.get("physical", {})
    if physical.get("flow_status") != "flow completed":
        errors.append("physical flow did not complete")
    if physical.get("source_match") is not True:
        errors.append("physical sources are not byte-identical to repaired sources")
    if physical.get("lvs_total_errors_from_report") != 0:
        errors.append("LVS is not clean")
    if physical.get("gds_present") is not True or physical.get("extracted_sta_present") is not True:
        errors.append("GDS or extracted STA evidence is missing")
    metrics = physical.get("metrics", {})
    for key in ("tritonRoute_violations", "Magic_violations", "lvs_total_errors"):
        if str(metrics.get(key)) != "0":
            errors.append(f"physical metric {key} is not zero")
    alignments = handoff.get("source_alignment", {})
    if not alignments or any(item.get("byte_identical") is not True for item in alignments.values()):
        errors.append("source alignment is incomplete")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    run_dir = Path(physical["run_dir"])
    metrics_path = run_dir / "reports/metrics.csv"
    row = next(csv.DictReader(metrics_path.open(encoding="utf-8")))
    print(json.dumps({"status": "passed", "design": handoff.get("design"), "lvs_errors": row.get("lvs_total_errors"), "sources": len(alignments), "model_generated": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
