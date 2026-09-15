#!/usr/bin/env python3
"""Independently verify the OpenROAD issue-bundle replay."""
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
    if report.get("schema_version") != "heldout-openroad-issue-bundle-replay-v1" or report.get("commit") != "7b6f366962eb093f7f76c136892a2950b9caebdb":
        errors.append("wrong schema or candidate")
    for name, item in report.get("source_snapshots", {}).items():
        source = path.parent / item.get("path", "")
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append(f"source digest mismatch: {name}")
    parent = report.get("parent_result", {})
    fixed = report.get("fixed_result", {})
    if parent.get("returncode") == 0:
        errors.append("parent runner unexpectedly worked after extraction")
    if fixed.get("returncode") != 0 or fixed.get("stdout", "").strip() != "portable":
        errors.append("fixed runner did not work from extraction directory")
    if report.get("contract", {}).get("package_installation_performed") is not False:
        errors.append("side-effect boundary is missing")
    if report.get("status") != "passed":
        errors.append("replay is not passed")
    result = {"schema_version": "heldout-openroad-issue-bundle-replay-check-v1", "status": "passed" if not errors else "blocked", "report": str(path), "errors": sorted(set(errors))}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
