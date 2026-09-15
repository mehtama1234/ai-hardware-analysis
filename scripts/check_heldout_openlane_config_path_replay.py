#!/usr/bin/env python3
"""Independently verify the second held-out OpenLane replay receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    path = args.report.resolve()
    errors: list[str] = []
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "errors": [str(exc)]}, sort_keys=True))
        return 1
    if report.get("report_sha256") != digest({k: v for k, v in report.items() if k != "report_sha256"}):
        errors.append("report digest mismatch")
    if report.get("schema_version") != "heldout-openlane-config-path-replay-v1" or report.get("commit") != "1c6d170484b830c650860153ac6407c17f626a84":
        errors.append("wrong schema or candidate")
    for name, item in report.get("source_snapshots", {}).items():
        source = path.parent / item.get("path", "")
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append(f"source digest mismatch: {name}")
    parent = report.get("parent_result", {})
    fixed = report.get("fixed_result", {})
    if parent.get("pdk_dir") == parent.get("expected_pdk") or parent.get("scl_dir") == parent.get("expected_scl"):
        errors.append("parent unexpectedly expanded one of the corrected path prefixes")
    if fixed.get("pdk_dir") != fixed.get("expected_pdk") or fixed.get("scl_dir") != fixed.get("expected_scl"):
        errors.append("fixed revision did not expand both path prefixes")
    if report.get("status") != "passed":
        errors.append("replay is not passed")
    result = {"schema_version": "heldout-openlane-config-path-replay-check-v1", "status": "passed" if not errors else "blocked", "report": str(path), "errors": sorted(set(errors))}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
