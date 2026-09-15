"""Validate draft or finalized verification-workbench usability results."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


TASKS = {
    "connect_and_prepare",
    "run_and_classify",
    "locate_root_cause",
    "review_repair",
    "compare_and_signoff",
}


def validate(payload: dict, *, finalized: bool = False) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if set(payload.get("tasks", [])) != TASKS:
        errors.append("tasks must contain exactly the five defined study tasks")
    participants = payload.get("participants", [])
    if not finalized:
        return errors
    if len(participants) < 3:
        errors.append("finalized study requires at least three participants")
    for index, participant in enumerate(participants, 1):
        if not isinstance(participant, dict):
            errors.append(f"participant {index} must be an object")
            continue
        results = participant.get("results", {})
        if set(results) != TASKS:
            errors.append(f"participant {index} must record all five task results")
        for task, result in results.items():
            if not isinstance(result, dict) or not isinstance(result.get("completed"), bool):
                errors.append(f"participant {index} task {task} needs boolean completed")
            if isinstance(result, dict) and not isinstance(result.get("minutes"), (int, float)):
                errors.append(f"participant {index} task {task} needs numeric minutes")
    aggregate = payload.get("aggregate", {})
    for field in ("completion_rate", "median_minutes_to_diagnosis", "wrong_run_selections", "unrecoverable_errors", "median_confidence_1_to_5"):
        if not isinstance(aggregate.get(field), (int, float)):
            errors.append(f"aggregate.{field} must be measured")
    digest = payload.get("evidence_bundle_sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
        errors.append("evidence_bundle_sha256 must be a 64-character SHA-256")
    if not isinstance(payload.get("lead_reviewer"), str) or not payload["lead_reviewer"].strip():
        errors.append("lead_reviewer is required")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--finalized", action="store_true")
    args = parser.parse_args()
    payload = json.loads(args.path.read_text(encoding="utf-8"))
    errors = validate(payload, finalized=args.finalized)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: usability study {'finalized' if args.finalized else 'draft'} ({args.path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
