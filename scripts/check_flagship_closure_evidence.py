#!/usr/bin/env python3
"""Independently check a self-contained flagship closure evidence bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REQUIRED = {"simulation", "mutation", "formal", "coverage", "security", "assertion_integrity"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    errors = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "errors": [str(exc)]}, sort_keys=True))
        return 1
    unsigned = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    if manifest.get("schema_version") != "flagship-closure-evidence-bundle-v1":
        errors.append("unsupported schema")
    if manifest.get("manifest_sha256") != hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()).hexdigest():
        errors.append("manifest digest mismatch")
    if manifest.get("status") != "passed":
        errors.append("bundle is not passed")
    roles = manifest.get("evidence", {})
    if set(manifest.get("required_roles", [])) != REQUIRED or set(roles) != REQUIRED:
        errors.append("required evidence roles are incomplete")
    aggregate = manifest.get("aggregate", {})
    aggregate_path = manifest_path.parent / aggregate.get("path", "")
    if not aggregate_path.is_file() or sha256(aggregate_path) != aggregate.get("sha256") or aggregate.get("all_passed") is not True:
        errors.append("aggregate copy is missing, modified, or not all_passed")
    for role, item in roles.items():
        path = manifest_path.parent / item.get("path", "")
        if not path.is_file():
            errors.append(f"missing evidence: {role}")
        elif sha256(path) != item.get("sha256"):
            errors.append(f"evidence digest mismatch: {role}")
    if "silicon signoff" not in manifest.get("claim_boundary", "").lower() or "production release" not in manifest.get("claim_boundary", "").lower():
        errors.append("claim boundary is missing local-only limit")
    result = {"schema_version": "flagship-closure-evidence-bundle-check-v1", "status": "passed" if not errors else "blocked", "manifest": str(manifest_path), "errors": sorted(set(errors))}
    result["check_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
