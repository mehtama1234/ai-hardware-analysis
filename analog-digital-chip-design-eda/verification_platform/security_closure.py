"""Adversarial hardware-security task and signoff contracts."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _digest(body: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_security_suite(suite: dict[str, Any]) -> None:
    if not isinstance(suite, dict) or suite.get("schema_version") != "security-task-suite-v1":
        raise ValueError("security task suite schema is unsupported")
    tasks = suite.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("security task suite requires non-empty tasks")
    seen: set[str] = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("security task must be an object")
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id or task_id in seen:
            raise ValueError("security task ids must be unique non-empty strings")
        seen.add(task_id)
        for key in ("threat_class", "source_revision", "origin_seed", "detection_mechanism"):
            if not isinstance(task.get(key), str) or not task[key].strip():
                raise ValueError(f"security task {task_id} requires {key}")


def evaluate_security_task(
    task: dict[str, Any],
    *,
    detected: bool,
    localized: bool,
    repaired_copy_passed: bool,
    regression_passed: bool,
    evidence: list[str],
    human_review: str = "review_required",
) -> dict[str, Any]:
    """Produce a signoff record that remains review-required by default."""
    validate_security_suite({"schema_version": "security-task-suite-v1", "tasks": [task]})
    if not isinstance(evidence, list) or not evidence or any(not isinstance(item, str) or not item.strip() for item in evidence):
        raise ValueError("security task requires non-empty evidence")
    if human_review not in {"review_required", "approved", "rejected"}:
        raise ValueError("human_review must be review_required, approved, or rejected")
    machine_checks = detected and localized and repaired_copy_passed and regression_passed
    status = "signed_off" if machine_checks and human_review == "approved" else "review_required" if machine_checks and human_review == "review_required" else "blocked"
    body: dict[str, Any] = {
        "schema_version": "security-signoff-record-v1",
        "task_id": task["task_id"],
        "threat_class": task["threat_class"],
        "source_revision": task["source_revision"],
        "origin_seed": task["origin_seed"],
        "detection_mechanism": task["detection_mechanism"],
        "detected": detected,
        "localized": localized,
        "repaired_copy_passed": repaired_copy_passed,
        "regression_passed": regression_passed,
        "machine_checks_passed": machine_checks,
        "human_review": human_review,
        "status": status,
        "evidence": evidence,
        "claim_boundary": "adversarial task result for the declared threat and regression scope; not a complete security certification",
    }
    body["record_sha256"] = _digest(body)
    return body
