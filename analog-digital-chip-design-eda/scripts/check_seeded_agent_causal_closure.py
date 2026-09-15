"""Independently validate the causal-localization repair-closure report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def validate(report: dict[str, object], *, require_full: bool = True) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != "seeded-agent-repair-closure-report-v3":
        errors.append("unsupported causal repair closure schema")
    tasks = report.get("tasks")
    if not isinstance(tasks, list) or not tasks or (require_full and (len(tasks) != 16 or report.get("task_count") != 16 or report.get("passed_tasks") != 16)):
        errors.append("causal repair closure must contain 16 passing tasks" if require_full else "causal repair closure must contain at least one task")
        tasks = tasks if isinstance(tasks, list) else []
    for task in tasks:
        if not isinstance(task, dict):
            errors.append("task record is not an object")
            continue
        required = {
            "baseline_status": "failed",
            "canonical_status": "passed",
            "localization_status": "available",
            "patch_candidate_status": "review_required",
            "patch_location_bound": True,
            "repaired_status": "passed",
            "canonical_unchanged": True,
            "passed": True,
        }
        for key, expected in required.items():
            if task.get(key) != expected:
                errors.append(f"{task.get('task_id', '<unknown>')} has invalid {key}")
        if not isinstance(task.get("localized_candidate_count"), int) or task["localized_candidate_count"] < 1:
            errors.append(f"{task.get('task_id', '<unknown>')} has no localized candidates")
    metrics = report.get("metrics")
    expected_metrics = {
        "canonical_reference_pass_rate": 1.0,
        "causal_localization_rate": 1.0,
        "source_bound_patch_rate": 1.0,
        "repair_retest_pass_rate": 1.0,
        "canonical_immutability_rate": 1.0,
        "end_to_end_closure_rate": 1.0,
    }
    if metrics != expected_metrics:
        errors.append("causal repair closure metrics do not report complete 16-task closure")
    expected_digest = hashlib.sha256(json.dumps({key: value for key, value in report.items() if key != "report_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if report.get("report_sha256") != expected_digest:
        errors.append("report_sha256 mismatch")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    errors = validate(report, require_full=not args.allow_partial)
    result = {"schema_version": "seeded-agent-causal-closure-check-v1", "status": "passed" if not errors else "blocked", "report": str(args.report), "errors": errors}
    result["check_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
