"""Independently validate the 100-mutant campaign and all child records."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _digest(body: dict) -> str:
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate(report: dict, root: Path) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != "mutation-closure-report-v1":
        errors.append("unsupported mutation report schema")
    if report.get("campaign") != "seeded-parameterized-100-mutant-campaign":
        errors.append("unexpected mutation campaign name")
    if report.get("total_mutations") != 100 or report.get("total_declared") != 100:
        errors.append("campaign does not declare exactly 100 mutations")
    if report.get("detected_mutations") != 100 or report.get("false_pass_count") != 0 or report.get("blocked_count") != 0 or report.get("mutation_score") != 1.0 or report.get("status") != "passed":
        errors.append("campaign aggregate does not show complete mutation closure")
    ids = report.get("mutation_ids")
    if not isinstance(ids, list) or len(ids) != 100 or len(set(ids)) != 100:
        errors.append("campaign mutation ids are missing or not unique")
    records = sorted(root.glob("*/mutation-result.json"))
    if len(records) != 100:
        errors.append(f"expected 100 mutation result files, found {len(records)}")
    observed_ids: list[str] = []
    for path in records:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            result = record.get("result", {})
            record_body = {key: value for key, value in record.items() if key != "record_sha256"}
            result_body = {key: value for key, value in result.items() if key != "result_sha256"}
            if record.get("record_sha256") != _digest(record_body):
                errors.append(f"record digest mismatch: {path}")
            if result.get("result_sha256") != _digest(result_body):
                errors.append(f"result digest mismatch: {path}")
            observed_ids.append(str(result.get("mutation_id")))
            for key in ("baseline_valid", "detected", "candidate_changed", "canonical_unchanged"):
                if result.get(key) is not True:
                    errors.append(f"mutation {result.get('mutation_id')} missing passing {key}")
            if result.get("false_pass") is not False:
                errors.append(f"mutation {result.get('mutation_id')} is a false pass")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"cannot read mutation record {path}: {error}")
    if ids is not None and sorted(str(item) for item in ids) != sorted(observed_ids):
        errors.append("report mutation ids do not match child records")
    by_source = report.get("by_source")
    if not isinstance(by_source, dict) or len(by_source) != 8 or any(item.get("mutation_score") != 1.0 or item.get("false_passes") != 0 or item.get("blocked") != 0 for item in by_source.values() if isinstance(item, dict)):
        errors.append("per-source mutation accounting is incomplete")
    expected = _digest({key: value for key, value in report.items() if key != "report_sha256"})
    if report.get("report_sha256") != expected:
        errors.append("mutation report digest mismatch")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    errors = validate(report, args.report.parent)
    result = {"schema_version": "mutation-campaign-check-v1", "status": "passed" if not errors else "blocked", "report": str(args.report), "errors": errors}
    result["check_sha256"] = _digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
