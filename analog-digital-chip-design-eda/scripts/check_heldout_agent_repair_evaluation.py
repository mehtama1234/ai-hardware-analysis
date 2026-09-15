#!/usr/bin/env python3
"""Independently validate a train/held-out agent repair evaluation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate(report: dict[str, object], *, require_model_selection: bool = False) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != "agent-repair-heldout-evaluation-report-v1":
        errors.append("unsupported held-out evaluation schema")
    expected_digest = digest({key: value for key, value in report.items() if key != "report_sha256"})
    if report.get("report_sha256") != expected_digest:
        errors.append("evaluation report digest mismatch")
    for split in ("train", "heldout"):
        score = report.get(split)
        run = report.get("runs", {}).get(split) if isinstance(report.get("runs"), dict) else None
        if not isinstance(score, dict) or not isinstance(run, dict):
            errors.append(f"missing {split} score or run")
            continue
        expected = score.get("expected_ids")
        observed = score.get("observed_ids")
        if not isinstance(expected, list) or not expected or observed != expected:
            errors.append(f"{split} task identity/order mismatch")
        if score.get("total") != len(expected or []) or score.get("passed") != len(expected or []):
            errors.append(f"{split} is not complete closure")
        if score.get("closure_rate") != 1.0 or score.get("all_passed") is not True:
            errors.append(f"{split} closure score is not 1.0")
        if require_model_selection and score.get("model_selected_repair_rate") != 1.0:
            errors.append(f"{split} does not prove model-selected repair fields")
        child = run.get("report")
        if not isinstance(child, dict) or child.get("status") != "passed":
            errors.append(f"{split} child report did not pass")
        child_digest = child.get("report_sha256") if isinstance(child, dict) else None
        if isinstance(child, dict) and child_digest != digest({key: value for key, value in child.items() if key != "report_sha256"}):
            errors.append(f"{split} child report digest mismatch")
    if report.get("status") != "passed":
        errors.append("evaluation status is not passed")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--require-real-backend", action="store_true")
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors = [str(error)]
        report = {}
    else:
        errors = validate(report, require_model_selection=args.require_real_backend)
        if args.require_real_backend and report.get("backend") != "local":
            errors.append("real-backend evaluation was required")
    result = {"schema_version": "agent-repair-heldout-evaluation-check-v1", "status": "passed" if not errors else "blocked", "report": str(args.report), "errors": sorted(set(errors))}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
