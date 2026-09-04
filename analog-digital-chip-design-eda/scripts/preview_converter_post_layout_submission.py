#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from submit_converter_post_layout_payload import DEFAULT_OUT_DIR, slug
from validate_converter_post_layout_payload import SCHEMA, load_json, validate_payload, validate_referenced_files
from validate_converter_post_layout_same_run import validate_same_run


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAYLOAD = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout" / "payload.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-submission-preview.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-submission-preview.md"


def placeholder_string(value: Any) -> bool:
    return isinstance(value, str) and ("replace-with" in value.lower() or "replace_with" in value.lower())


def issue_category(issue: str) -> str:
    if "must point to an existing file" in issue or "must list existing files" in issue:
        return "missing_file"
    if issue.startswith("missing "):
        return "missing_field"
    if "must equal provenance.run_id" in issue or "run_id" in issue:
        return "same_run_identity"
    if "template" in issue:
        return "template_boundary"
    if "must be positive" in issue or "must be numeric" in issue:
        return "numeric_boundary"
    return "strict_boundary"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def collect_issues(payload: dict[str, Any], payload_path: Path) -> list[str]:
    schema = load_json(SCHEMA)
    issues = validate_payload(payload, schema)
    issues.extend(validate_referenced_files(payload, payload_path))
    issues.extend(validate_same_run(payload))
    if payload.get("template_only") is True:
        issues.append("template payloads cannot be submitted")
    return issues


def build_report(payload_path: Path, output_dir: Path) -> dict[str, Any]:
    payload = load_json(payload_path)
    issues = collect_issues(payload, payload_path)
    converter_id = payload.get("converter_id")
    converter_id_ready = isinstance(converter_id, str) and bool(converter_id.strip()) and not placeholder_string(converter_id)
    output_slug = slug(converter_id) if converter_id_ready else "blocked-until-real-converter-id"
    would_write_dir = output_dir.resolve()
    ready = not issues
    return {
        "result_type": "converter_post_layout_submission_preview",
        "status": "ready_to_submit_without_writing" if ready else "blocked_before_submission",
        "source_payload": rel(payload_path),
        "output_dir": rel(would_write_dir),
        "converter_id_ready": converter_id_ready,
        "would_write_accepted_evidence": ready,
        "would_write_files": [
            rel(would_write_dir / f"{output_slug}.break-even-rerun.json"),
            rel(would_write_dir / f"{output_slug}.submission-report.json"),
        ],
        "submission_command": f"python3 scripts/submit_converter_post_layout_payload.py {rel(payload_path)}",
        "strict_issue_count": len(issues),
        "strict_issues": [{"category": issue_category(issue), "message": issue} for issue in issues],
        "claim_boundary": {
            "allowed": "previews strict submission blockers and the accepted evidence file names without writing accepted evidence",
            "not_allowed": "does not submit evidence, does not create accepted-post-layout, does not run break-even, and does not prove post-layout converter replacement",
        },
    }


def write_markdown(report: dict[str, Any], output: Path) -> None:
    lines = [
        "# Converter Post-Layout Submission Preview",
        "",
        f"- status: `{report['status']}`",
        f"- source payload: `{report['source_payload']}`",
        f"- output dir: `{report['output_dir']}`",
        f"- converter id ready: `{report['converter_id_ready']}`",
        f"- would write accepted evidence: `{report['would_write_accepted_evidence']}`",
        f"- strict issue count: `{report['strict_issue_count']}`",
        "",
        "This preview answers one practical question before submission: if the strict submitter ran on this payload, would it write accepted evidence, and which files would it write?",
        "",
        "## First Principle",
        "",
        "Submission should be boring. The only time it should create accepted evidence is when the payload already names one real converter, one real run, real referenced files, and real numeric values. A preview step lets a reviewer inspect that boundary without creating the accepted directory.",
        "",
        "## Would Write Files",
        "",
        *[f"- `{path}`" for path in report["would_write_files"]],
        "",
        "## Submission Command",
        "",
        f"`{report['submission_command']}`",
        "",
        "## Strict Issues",
        "",
    ]
    if report["strict_issues"]:
        lines.extend(f"- `{issue['category']}`: {issue['message']}" for issue in report["strict_issues"])
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    output.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview converter post-layout strict submission without writing accepted evidence.")
    parser.add_argument("--payload", type=Path, default=DEFAULT_PAYLOAD)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--json-output", type=Path, default=OUT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=OUT_MD)
    parser.add_argument("--expect-blocked", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload_path = args.payload.resolve()
    if not payload_path.exists():
        raise SystemExit(f"payload not found: {payload_path}")
    report = build_report(payload_path, args.output_dir)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, args.markdown_output)
    if args.expect_blocked and report["would_write_accepted_evidence"]:
        raise SystemExit("submission preview unexpectedly ready")
    print("converter_post_layout_submission_preview")
    print(f"status,{report['status']}")
    print(f"would_write_accepted_evidence,{report['would_write_accepted_evidence']}")
    print(f"strict_issue_count,{report['strict_issue_count']}")
    print(f"json,{args.json_output}")
    print(f"markdown,{args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
