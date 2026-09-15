#!/usr/bin/env python3
"""Independently validate the native OpenROAD FIFO repair closure."""
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
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors = [str(error)]
        report = {}
    else:
        errors = []
        if report.get("schema_version") != "openroad-fifo-agent-repair-closure-report-v1":
            errors.append("unsupported report schema")
        for key, expected in {
            "repository": "OpenROAD-flow-scripts", "repository_revision": "be0dca0b1",
            "task_id": "openroad-fifo-reset-empty", "baseline_status": "failed",
            "agent_status": "available", "patch_candidate_status": "review_required",
            "repaired_status": "passed", "canonical_unchanged": True, "status": "passed",
        }.items():
            if report.get(key) != expected:
                errors.append(f"{key} does not match expected closure value")
        expected_digest = digest({key: value for key, value in report.items() if key != "report_sha256"})
        if report.get("report_sha256") != expected_digest:
            errors.append("report digest mismatch")
    result = {"schema_version": "openroad-fifo-agent-repair-closure-check-v1", "status": "passed" if not errors else "blocked", "report": str(args.report), "errors": sorted(set(errors))}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
