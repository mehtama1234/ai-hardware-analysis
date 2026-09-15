"""Independently validate the historical OpenLane GUI repair report."""

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
    report = json.loads(args.report.read_text(encoding="utf-8"))
    errors = []
    if report.get("schema_version") != "openlane-historical-gui-agent-repair-report-v1":
        errors.append("schema version mismatch")
    for key, expected in {
        "repository": "OpenLane", "repository_revision": "ff5509f6",
        "historical_fix_commit": "fe0ba006", "source_file": "gui.py",
        "baseline_status": "failed", "agent_status": "available",
        "patch_candidate_status": "review_required", "repaired_status": "passed",
        "status": "passed", "canonical_unchanged": True,
    }.items():
        if report.get(key) != expected:
            errors.append(f"{key} expected {expected!r}, got {report.get(key)!r}")
    recorded = report.get("report_sha256")
    unsigned = dict(report)
    unsigned.pop("report_sha256", None)
    if recorded != digest(unsigned):
        errors.append("report digest mismatch")
    result = {"schema_version": "openlane-historical-gui-agent-repair-check-v1", "status": "passed" if not errors else "blocked", "errors": errors, "report": str(args.report)}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
