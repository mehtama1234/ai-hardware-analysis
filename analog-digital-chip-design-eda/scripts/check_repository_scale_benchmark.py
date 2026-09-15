#!/usr/bin/env python3
"""Independently validate a repository-scale benchmark report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SCHEMA = "repository-scale-benchmark-report-v1"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check_snapshot(snapshot: object, label: str, errors: list[str]) -> None:
    if not isinstance(snapshot, dict):
        errors.append(f"{label} is not an object")
        return
    expected = snapshot.get("snapshot_sha256")
    body = dict(snapshot)
    body.pop("snapshot_sha256", None)
    if not isinstance(expected, str) or digest(body) != expected:
        errors.append(f"{label} digest mismatch")
    if not isinstance(snapshot.get("files"), list):
        errors.append(f"{label} has no file list")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "blocked", "errors": [str(error)]}, sort_keys=True))
        return 1

    if not isinstance(report, dict):
        print(json.dumps({"status": "blocked", "errors": ["report is not an object"]}, sort_keys=True))
        return 1
    expected_report = report.get("report_sha256")
    body = dict(report)
    body.pop("report_sha256", None)
    if report.get("schema_version") != SCHEMA:
        errors.append("schema mismatch")
    if not isinstance(expected_report, str) or digest(body) != expected_report:
        errors.append("report digest mismatch")
    records = report.get("records")
    if not isinstance(records, list) or not records:
        errors.append("records are missing")
        records = []
    if report.get("task_count") != len(records):
        errors.append("task count mismatch")
    if report.get("status") != "passed":
        errors.append("benchmark is not passed")

    task_ids: set[str] = set()
    for index, record in enumerate(records):
        prefix = f"record[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix} is not an object")
            continue
        task_id = record.get("task_id")
        if not isinstance(task_id, str) or not task_id or task_id in task_ids:
            errors.append(f"{prefix} has a duplicate or missing task id")
        else:
            task_ids.add(task_id)
        expected_record = record.get("record_sha256")
        record_body = dict(record)
        record_body.pop("record_sha256", None)
        if not isinstance(expected_record, str) or digest(record_body) != expected_record:
            errors.append(f"{prefix} digest mismatch")
        if record.get("status") != "passed":
            errors.append(f"{prefix} is not passed")
        check_snapshot(record.get("source_snapshot_before"), f"{prefix}.source_snapshot_before", errors)
        check_snapshot(record.get("source_snapshot_after"), f"{prefix}.source_snapshot_after", errors)
        check_snapshot(record.get("candidate_snapshot_after"), f"{prefix}.candidate_snapshot_after", errors)
        result = record.get("result")
        if not isinstance(result, dict) or result.get("status") != "passed":
            errors.append(f"{prefix} result is not passed")
            continue
        expected_result = result.get("result_sha256")
        result_body = dict(result)
        result_body.pop("result_sha256", None)
        if not isinstance(expected_result, str) or digest(result_body) != expected_result:
            errors.append(f"{prefix} result digest mismatch")
        checks = result.get("checks")
        if not isinstance(checks, dict) or any(value is not True for key, value in checks.items() if key != "unexpected_changed_files"):
            errors.append(f"{prefix} result checks are not all true")
        if isinstance(checks, dict) and checks.get("unexpected_changed_files") != []:
            errors.append(f"{prefix} has unexpected changed files")

    output = {
        "schema_version": "repository-scale-benchmark-check-v1",
        "report": str(args.report),
        "status": "passed" if not errors else "blocked",
        "task_count": len(records),
        "errors": sorted(set(errors)),
    }
    output["check_sha256"] = digest(output)
    print(json.dumps(output, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
