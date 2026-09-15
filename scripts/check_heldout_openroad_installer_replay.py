#!/usr/bin/env python3
"""Independently verify the held-out OpenROAD installer replay."""
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
    if report.get("schema_version") != "heldout-openroad-installer-replay-v1" or report.get("commit") != "83e9302b0fce4745d7e14f58145849513169c94a":
        errors.append("wrong schema or candidate")
    for name, item in report.get("source_snapshots", {}).items():
        source = path.parent / item.get("path", "")
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != item.get("sha256"):
            errors.append(f"source digest mismatch: {name}")
    parent = report.get("parent_result", {})
    fixed = report.get("fixed_result", {})
    if not parent.get("resolved_lockfile", "").endswith("/parent/requirements-common_lock.txt"):
        errors.append("parent did not resolve the pre-cd relative lockfile")
    if not fixed.get("resolved_lockfile", "").endswith("/fixed/etc/requirements-common_lock.txt"):
        errors.append("fixed revision did not resolve the absolute script-relative lockfile")
    if report.get("contract", {}).get("package_installation_performed") is not False:
        errors.append("side-effect boundary is missing")
    if report.get("status") != "passed":
        errors.append("replay is not passed")
    result = {"schema_version": "heldout-openroad-installer-replay-check-v1", "status": "passed" if not errors else "blocked", "report": str(path), "errors": sorted(set(errors))}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
