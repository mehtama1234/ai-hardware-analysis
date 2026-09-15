"""Independently validate the integrated formal-proof closure suite."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(body: dict) -> str:
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate(report: dict, root: Path) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != "formal-proof-closure-suite-report-v1":
        errors.append("unsupported formal closure suite schema")
    results = report.get("results")
    if not isinstance(results, list) or len(results) != 3:
        errors.append("formal closure suite must contain exactly three results")
        results = results if isinstance(results, list) else []
    if report.get("total") != len(results) or report.get("all_proven") is not True:
        errors.append("formal closure suite aggregate is incomplete")
    ids = [item.get("property_id") for item in results if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        errors.append("formal closure property ids are not unique")
    for item in results:
        if not isinstance(item, dict) or item.get("proof_status") != "proven":
            errors.append(f"formal closure result is not proven: {item}")
            continue
        path = root / str(item.get("closure", ""))
        if not path.is_file():
            errors.append(f"missing formal closure record: {path}")
            continue
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            closure = record.get("closure", {})
            audit = record.get("assumption_audit", {})
            if not all(key in record for key in ("bounded", "inductive", "assumption_reachability", "assumption_audit", "closure")):
                errors.append(f"formal closure record is incomplete: {path}")
            if closure.get("proof_status") != "proven" or audit.get("status") != "passed":
                errors.append(f"formal closure record is not proven: {path}")
            if audit.get("audit_sha256") != digest({key: value for key, value in audit.items() if key != "audit_sha256"}):
                errors.append(f"assumption audit digest mismatch: {path}")
            if closure.get("result_sha256") != digest({key: value for key, value in closure.items() if key != "result_sha256"}):
                errors.append(f"formal closure digest mismatch: {path}")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"cannot read formal closure record {path}: {error}")
    if report.get("report_sha256") != digest({key: value for key, value in report.items() if key != "report_sha256"}):
        errors.append("formal closure suite report digest mismatch")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    errors = validate(report, args.report.parent)
    result = {"schema_version": "formal-proof-closure-suite-check-v1", "status": "passed" if not errors else "blocked", "report": str(args.report), "errors": errors}
    result["check_sha256"] = digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
