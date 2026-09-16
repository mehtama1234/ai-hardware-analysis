#!/usr/bin/env python3
"""Independently check the flagship pending human-review receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    errors = []
    receipt_path = args.receipt.resolve(); manifest_path = args.manifest.resolve()
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8")); manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "errors": [str(exc)]}, sort_keys=True)); return 1
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if receipt.get("schema_version") != "flagship-human-review-receipt-v1": errors.append("unsupported receipt schema")
    if receipt.get("receipt_sha256") != digest(unsigned): errors.append("receipt digest mismatch")
    status = receipt.get("status")
    decision = receipt.get("decision")
    reviewer = receipt.get("reviewer")
    valid_pending = status == "pending_human_review" and receipt.get("approval") is False and reviewer is None
    valid_decision = status in {"human_approved", "human_rejected"} and decision in {"approve", "reject"} and reviewer is not None and bool(str(reviewer).strip()) and receipt.get("approval") is (decision == "approve") and status == ("human_approved" if decision == "approve" else "human_rejected") and bool(str(receipt.get("decision_scope", "")).strip()) and bool(str(receipt.get("decision_reason", "")).strip())
    if not (valid_pending or valid_decision): errors.append("receipt is neither a valid pending record nor an explicit human decision")
    if receipt.get("reviewed_manifest", {}).get("sha256") != manifest.get("manifest_sha256"): errors.append("receipt is not bound to the current flagship manifest")
    expected_manifest_path = str(Path(".artifacts") / manifest_path.name)
    if receipt.get("reviewed_manifest", {}).get("path") != expected_manifest_path: errors.append("receipt manifest path is not repository-relative")
    if receipt.get("reviewed_evidence_sha256") != digest(manifest.get("evidence", [])): errors.append("receipt evidence digest mismatch")
    if manifest.get("release_decision") != "blocked_pending_physical_and_measured_gates" or manifest.get("analog_authorized") is not False: errors.append("receipt target is not fail-closed")
    boundary = receipt.get("claim_boundary", "").lower()
    if valid_pending and "not human approval" not in boundary: errors.append("pending receipt claim boundary is too broad")
    if valid_decision and "does not authorize" not in boundary: errors.append("decision receipt claim boundary is too broad")
    result = {"schema_version": "flagship-human-review-receipt-check-v1", "status": "passed" if not errors else "blocked", "receipt": str(receipt_path), "manifest": str(manifest_path), "errors": sorted(set(errors))}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True)); return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
