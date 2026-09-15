#!/usr/bin/env python3
"""Independently verify the held-out behavioral-contract inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    expected = report.pop("report_sha256", None)
    errors = []
    if expected != digest(report):
        errors.append("report digest mismatch")
    if report.get("schema_version") != "heldout-behavioral-contract-inventory-v1":
        errors.append("schema mismatch")
    targets = report.get("targets", [])
    if report.get("target_count") != len(targets):
        errors.append("target count mismatch")
    if report.get("compiled_target_count") != sum(item.get("compiled") is True for item in targets):
        errors.append("compiled count mismatch")
    available = sum(item.get("behavioral_contract_status") == "available" for item in targets)
    if report.get("behavioral_contract_count") != available:
        errors.append("behavioral contract count mismatch")
    if report.get("missing_behavioral_contract_count") != len(targets) - available:
        errors.append("missing contract count mismatch")
    if report.get("status") != ("ready_for_heldout_execution" if available == len(targets) else "blocked_pending_behavioral_contracts"):
        errors.append("status does not match inventory")
    if "compile and structural evidence" not in report.get("claim_boundary", ""):
        errors.append("claim boundary missing compile limitation")
    result = {"schema_version": "heldout-behavioral-contract-inventory-check-v1", "status": "passed" if not errors else "blocked", "report": str(args.report.resolve()), "behavioral_contract_count": available, "missing_behavioral_contract_count": len(targets) - available, "errors": sorted(set(errors))}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
