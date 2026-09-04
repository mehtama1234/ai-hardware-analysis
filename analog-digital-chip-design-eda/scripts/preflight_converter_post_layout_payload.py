#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_converter_post_layout_same_run import validate_same_run
from validate_converter_post_layout_payload import SCHEMA, load_json, validate_payload, validate_referenced_files


ROOT = Path(__file__).resolve().parents[1]


def classify_issue(issue: str) -> str:
    if "must point to an existing file" in issue or "must list existing files" in issue:
        return "missing_file"
    if issue.startswith("missing "):
        return "missing_field"
    if "noise" in issue:
        return "noise_boundary"
    if "sharing." in issue:
        return "sharing_boundary"
    if "must be positive" in issue or "must be numeric" in issue:
        return "numeric_boundary"
    return "claim_boundary"


def build_report(payload_path: Path) -> dict[str, Any]:
    schema = load_json(SCHEMA)
    payload = load_json(payload_path)
    shape_issues = validate_payload(payload, schema)
    file_issues = validate_referenced_files(payload, payload_path)
    same_run_issues = validate_same_run(payload)
    if payload.get("template_only") is True:
        shape_issues.append("template payloads cannot be submitted")
    issues = shape_issues + file_issues + same_run_issues
    return {
        "result_type": "converter_post_layout_payload_preflight",
        "source_payload": str(payload_path),
        "status": "ready_for_strict_submission" if not issues else "not_ready_for_strict_submission",
        "shape_validation_passed": not shape_issues,
        "referenced_file_validation_passed": not file_issues,
        "same_run_validation_passed": not same_run_issues,
        "issue_count": len(issues),
        "issues": [{"category": classify_issue(issue), "message": issue} for issue in issues],
        "submission_command_if_ready": f"python3 scripts/submit_converter_post_layout_payload.py {payload_path}",
        "claim_boundary": {
            "allowed": "explains whether a candidate payload is ready for strict submission",
            "not_allowed": "does not import the payload, does not write accepted evidence, and does not replace converter break-even assumptions",
        },
    }


def write_markdown(report: dict[str, Any], output: Path) -> None:
    lines = [
        "# Converter Post-Layout Payload Preflight",
        "",
        f"- status: `{report['status']}`",
        f"- source payload: `{report['source_payload']}`",
        f"- shape validation passed: `{report['shape_validation_passed']}`",
        f"- referenced file validation passed: `{report['referenced_file_validation_passed']}`",
        f"- same-run validation passed: `{report['same_run_validation_passed']}`",
        f"- issue count: `{report['issue_count']}`",
        "",
        "Preflight is a review step. It reads the candidate package and explains whether the payload is ready for strict submission. It does not write accepted evidence.",
        "",
        "## First Principle",
        "",
        "A real converter package has to connect a number to the thing that made the number. Energy must come from the converter being claimed. Latency must come from the same conversion path. Noise must be below the same output boundary. Area must belong to the same ADC and DAC objects. The sharing rule must match the break-even calculation.",
        "",
        "The preflight report separates three mistakes. A shape mistake means the payload is not saying enough. A file mistake means the payload says the right kind of thing, but the evidence cannot be inspected. A same-run mistake means the values are not tied to one experiment or one post-layout simulation.",
        "",
        "## Issues",
        "",
    ]
    if report["issues"]:
        for issue in report["issues"]:
            lines.append(f"- `{issue['category']}`: {issue['message']}")
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Next Command If Ready",
        "",
        f"`{report['submission_command_if_ready']}`",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    output.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight a converter post-layout payload without submitting it.")
    parser.add_argument("payload", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--expect-ready", action="store_true")
    parser.add_argument("--expect-not-ready", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload_path = args.payload.resolve()
    if not payload_path.exists():
        raise SystemExit(f"payload not found: {payload_path}")
    report = build_report(payload_path)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(report, args.markdown_output)

    ready = report["status"] == "ready_for_strict_submission"
    if args.expect_ready and not ready:
        print("FAIL converter_post_layout_payload_preflight", file=sys.stderr)
        print(f"status,{report['status']}", file=sys.stderr)
        print(f"issues,{report['issue_count']}", file=sys.stderr)
        return 1
    if args.expect_not_ready and ready:
        print("FAIL converter_post_layout_payload_preflight: payload unexpectedly ready", file=sys.stderr)
        return 1

    print("PASS converter_post_layout_payload_preflight")
    print(f"payload,{payload_path}")
    print(f"status,{report['status']}")
    print(f"issues,{report['issue_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
