"""Independently validate the adversarial register-policy campaign report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _digest(body: dict) -> str:
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate(report: dict, root: Path) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != "security-campaign-report-v1":
        errors.append("unsupported security campaign schema")
    tasks = report.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != 8:
        errors.append("security campaign must contain exactly eight task records")
        tasks = tasks if isinstance(tasks, list) else []
    if report.get("total") != len(tasks):
        errors.append("security campaign total does not match task records")
    ids = [item.get("task_id") for item in tasks if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        errors.append("security campaign task ids are not unique")
    for item in tasks:
        if not isinstance(item, dict):
            errors.append("security campaign task record is not an object")
            continue
        if item.get("status") != "review_required":
            errors.append(f"task is not review_required: {item.get('task_id')}")
        for key in ("machine_checks_passed", "canonical_unchanged", "mutant_changed", "repaired_matches_canonical"):
            if item.get(key) is not True:
                errors.append(f"task {item.get('task_id')} missing passing {key}")
        record_path = root / str(item.get("record", ""))
        if not record_path.is_file():
            errors.append(f"missing security signoff record: {record_path}")
            continue
        try:
            signoff = json.loads(record_path.read_text(encoding="utf-8"))
            body = {key: value for key, value in signoff.items() if key != "record_sha256"}
            if signoff.get("record_sha256") != _digest(body):
                errors.append(f"security signoff digest mismatch: {item.get('task_id')}")
            if signoff.get("task_id") != item.get("task_id") or signoff.get("status") != "review_required":
                errors.append(f"security signoff identity/status mismatch: {item.get('task_id')}")
            if signoff.get("machine_checks_passed") is not True:
                errors.append(f"security signoff machine checks did not pass: {item.get('task_id')}")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"cannot read security signoff {record_path}: {error}")
    expected = _digest({key: value for key, value in report.items() if key != "report_sha256"})
    if report.get("report_sha256") != expected:
        errors.append("security campaign report digest mismatch")
    if report.get("all_machine_checks_passed") is not True or report.get("all_review_required") is not True:
        errors.append("security campaign aggregate flags are not passing")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    errors = validate(report, args.report.parent)
    result = {"schema_version": "security-campaign-check-v1", "status": "passed" if not errors else "blocked", "report": str(args.report), "errors": errors}
    result["check_sha256"] = _digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
