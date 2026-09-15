#!/usr/bin/env python3
"""Independently verify the first held-out OpenLane replay receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report_path = args.report.resolve()
    errors: list[str] = []
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "errors": [str(exc)]}, sort_keys=True))
        return 1
    unsigned = {key: value for key, value in report.items() if key != "report_sha256"}
    if report.get("report_sha256") != digest(unsigned):
        errors.append("report digest mismatch")
    if report.get("schema_version") != "heldout-openlane-historical-replay-v1":
        errors.append("schema mismatch")
    if report.get("repository") != "OpenLane" or report.get("commit") != "000c992a07a3b45db65db2e6559125fd94dd77df":
        errors.append("wrong held-out candidate")
    snapshots = report.get("source_snapshots", {})
    for name, item in snapshots.items():
        path = report_path.parent / item.get("path", "")
        if not path.is_file() or sha256(path) != item.get("sha256"):
            errors.append(f"snapshot digest mismatch: {name}")
    contract = report.get("regression_contract", {})
    if contract != {
        "active_netlist_contains_assign": True,
        "synthesis_results_netlist_contains_assign": False,
        "parent_call_uses_active_netlist": False,
        "fixed_call_uses_active_netlist": True,
    }:
        errors.append("regression contract mismatch")
    baseline = report.get("baseline", {})
    repaired = report.get("repaired", {})
    if baseline.get("catch_returncode") != 0:
        errors.append("buggy parent did not silently pass the wrong path")
    if repaired.get("catch_returncode") == 0:
        errors.append("fixed checker did not reject the active assign")
    parent = (report_path.parent / "parent-synthesis.tcl").read_text(encoding="utf-8") if (report_path.parent / "parent-synthesis.tcl").is_file() else ""
    fixed = (report_path.parent / "fixed-synthesis.tcl").read_text(encoding="utf-8") if (report_path.parent / "fixed-synthesis.tcl").is_file() else ""
    if "check_assign_statements\n" not in parent:
        errors.append("parent caller is not the no-argument call")
    if "check_assign_statements $::env(CURRENT_NETLIST)" not in fixed:
        errors.append("fixed caller is not bound to CURRENT_NETLIST")
    if report.get("status") != "passed":
        errors.append("replay is not passed")
    result = {"schema_version": "heldout-openlane-historical-replay-check-v1", "status": "passed" if not errors else "blocked", "report": str(report_path), "errors": sorted(set(errors))}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
