#!/usr/bin/env python3
"""Independently check the AIMC mutation repair/retest evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    errors = []
    if report.get("schema_version") not in {"aimc-mutation-repair-retest-v1", "aimc-mutation-repair-retest-v2"}:
        errors.append("unexpected schema")
    if report.get("status") != "passed":
        errors.append("repair/retest did not pass")
    if report.get("approval", {}).get("status") != "approved":
        errors.append("approval record is missing")
    if report.get("simulation", {}).get("pass_marker_present") is not True:
        errors.append("AIMC simulation PASS marker is missing")
    if report.get("physical_revalidation", {}).get("status") != "passed":
        errors.append("physical-input revalidation did not pass")
    alignments = report.get("source_alignment", {})
    if len(alignments) != 7:
        errors.append("expected seven aligned RTL inputs")
    for name, item in alignments.items():
        if item.get("canonical_match") is not True or item.get("physical_input_match") is not True:
            errors.append(f"{name} is not aligned to canonical and physical inputs")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(json.dumps({"status": "passed", "sources": len(alignments), "physical_revalidation": "passed"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
