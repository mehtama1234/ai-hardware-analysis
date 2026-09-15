"""Independently validate a real-model Colab run before crediting it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _digest(body: dict) -> str:
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate(report: dict, summary: dict) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != "next-stage-colab-report-v1":
        errors.append("unsupported Colab report schema")
    if report.get("agent_backend") != "local":
        errors.append("Colab report did not use the local real-model backend")
    if report.get("all_machine_stages_passed") is not True:
        errors.append("Colab machine stages did not all pass")
    expected_report = _digest({key: value for key, value in report.items() if key != "report_sha256"})
    if report.get("report_sha256") != expected_report:
        errors.append("Colab report digest mismatch")
    steps = summary.get("steps")
    if not isinstance(steps, list) or len(steps) < 3:
        errors.append("Colab summary lacks GPU, dependency, and model-download steps")
    else:
        for index, name in enumerate(("gpu-probe", "dependencies", "model-download")):
            if steps[index].get("status") != "passed":
                errors.append(f"Colab {name} did not pass")
    if summary.get("status") != "passed":
        errors.append("remote Colab summary is not passed")
    expected_summary = _digest({key: value for key, value in summary.items() if key != "summary_sha256"})
    if summary.get("summary_sha256") != expected_summary:
        errors.append("Colab summary digest mismatch")
    if summary.get("report", {}).get("report_sha256") != report.get("report_sha256"):
        errors.append("Colab summary report does not match downloaded report")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("summary", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    errors = validate(report, summary)
    result = {"schema_version": "next-stage-real-colab-check-v1", "status": "passed" if not errors else "blocked", "report": str(args.report), "summary": str(args.summary), "errors": errors}
    result["check_sha256"] = _digest(result)
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
