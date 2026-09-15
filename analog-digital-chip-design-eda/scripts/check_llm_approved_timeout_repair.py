#!/usr/bin/env python3
"""Independently verify the approved seeded-timeout repair."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", type=Path)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.review.read_text(encoding="utf-8"))
    errors = []
    if report.get("schema_version") != "llm-approved-timeout-repair-v1": errors.append("unexpected schema")
    if report.get("repair", {}).get("model_generated") is not True: errors.append("repair is not model-generated")
    if report.get("repair", {}).get("before") != "  assign timed_out = count >= 3'd4;" or report.get("repair", {}).get("after") != "  assign timed_out = count >= 3'd3;": errors.append("wrong threshold edit")
    if report.get("approval", {}).get("status") not in {"approved", "rejected"}: errors.append("approval missing or invalid")
    if report.get("retest", {}).get("status") != "passed": errors.append("retest failed")
    if report.get("retest", {}).get("original_unchanged") is not True: errors.append("canonical source changed")
    if report.get("source", {}).get("sha256") != digest(args.source): errors.append("canonical source hash mismatch")
    scope = report.get("verification_scope", {})
    approval = report.get("approval", {})
    if approval.get("source_sha256") != report.get("source", {}).get("sha256"): errors.append("approval is not bound to source")
    if approval.get("scope_sha256") != scope.get("scope_sha256"): errors.append("approval is not bound to scope")
    if scope.get("scope_sha256") != object_digest({key: value for key, value in scope.items() if key != "scope_sha256"}): errors.append("verification scope digest is invalid")
    if report.get("retest", {}).get("formal", {}).get("status") != "passed": errors.append("formal retest is missing or did not pass")
    if errors:
        for error in errors: print(f"ERROR: {error}")
        return 1
    print(json.dumps({"status": "passed", "design": "seeded_timeout", "model_generated": True, "canonical_source_unchanged": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
