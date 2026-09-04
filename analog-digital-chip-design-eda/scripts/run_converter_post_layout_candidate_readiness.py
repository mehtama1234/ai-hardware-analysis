#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAYLOAD = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout" / "payload.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-readiness-run.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-readiness-run.md"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the converter post-layout candidate readiness chain without submitting evidence.")
    parser.add_argument("--payload", type=Path, default=DEFAULT_PAYLOAD)
    parser.add_argument("--json-output", type=Path, default=OUT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=OUT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = args.payload.resolve()
    workspace = payload.parent
    preflight_json = args.json_output.with_name("converter-post-layout-candidate-readiness-preflight.json")
    preflight_md = args.markdown_output.with_name("converter-post-layout-candidate-readiness-preflight.md")

    audit_run = run([
        sys.executable,
        "scripts/audit_converter_post_layout_candidate_workspace.py",
        "--workspace",
        str(workspace),
    ])
    checklist_run = run([sys.executable, "scripts/generate_converter_post_layout_candidate_fill_checklist.py"])
    progress_run = run([sys.executable, "scripts/generate_converter_post_layout_candidate_progress_report.py"])
    preflight_run = run([
        sys.executable,
        "scripts/preflight_converter_post_layout_payload.py",
        str(payload),
        "--json-output",
        str(preflight_json),
        "--markdown-output",
        str(preflight_md),
    ])

    audit = load_json(ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-workspace-audit.json")
    checklist = load_json(ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-fill-checklist.json")
    progress = load_json(ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-progress-report.json")
    preflight = load_json(preflight_json)
    ready_for_submission = preflight_run.returncode == 0 and preflight.get("status") == "ready_for_strict_submission"
    report = {
        "result_type": "converter_post_layout_candidate_readiness_run",
        "status": "candidate_ready_for_strict_submission" if ready_for_submission else "candidate_not_ready_for_strict_submission",
        "payload": rel(payload),
        "workspace": rel(workspace),
        "audit_status": audit.get("status"),
        "checklist_status": checklist.get("status"),
        "progress_status": progress.get("status"),
        "preflight_status": preflight.get("status"),
        "placeholder_count": audit.get("placeholder_count"),
        "missing_or_unresolved_file_count": audit.get("missing_or_unresolved_file_count"),
        "open_checklist_items": progress.get("open_checklist_items"),
        "preflight_issue_count": preflight.get("issue_count"),
        "ready_for_strict_submission": ready_for_submission,
        "commands": {
            "audit": "python3 scripts/audit_converter_post_layout_candidate_workspace.py",
            "checklist": "python3 scripts/generate_converter_post_layout_candidate_fill_checklist.py",
            "progress": "python3 scripts/generate_converter_post_layout_candidate_progress_report.py",
            "preflight": f"python3 scripts/preflight_converter_post_layout_payload.py {rel(payload)}",
            "submit_if_ready": f"python3 scripts/submit_converter_post_layout_payload.py {rel(payload)}",
        },
        "returncodes": {
            "audit": audit_run.returncode,
            "checklist": checklist_run.returncode,
            "progress": progress_run.returncode,
            "preflight": preflight_run.returncode,
        },
        "claim_boundary": {
            "allowed": "runs audit, checklist, progress, and preflight to decide whether strict submission may start",
            "not_allowed": "does not submit evidence, does not write accepted post-layout artifacts, and does not prove converter physics",
        },
    }
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Candidate Readiness Run",
        "",
        f"- status: `{report['status']}`",
        f"- payload: `{report['payload']}`",
        f"- workspace: `{report['workspace']}`",
        f"- audit status: `{report['audit_status']}`",
        f"- checklist status: `{report['checklist_status']}`",
        f"- progress status: `{report['progress_status']}`",
        f"- preflight status: `{report['preflight_status']}`",
        f"- placeholder count: `{report['placeholder_count']}`",
        f"- missing or unresolved file count: `{report['missing_or_unresolved_file_count']}`",
        f"- open checklist items: `{report['open_checklist_items']}`",
        f"- preflight issue count: `{report['preflight_issue_count']}`",
        f"- ready for strict submission: `{report['ready_for_strict_submission']}`",
        "",
        "This is the one-command readiness path for the candidate post-layout package. It refreshes the workspace audit, fill checklist, progress report, and preflight result. It stops before submission.",
        "",
        "## First Principle",
        "",
        "A real converter package should move through four questions in order. Does the workspace still contain placeholders? Does the checklist have open fields or files? Does the short progress state say the packet is ready? Does preflight agree that strict submission may start?",
        "",
        "Only when all four answers are clean should the submission command run.",
        "",
        "## Commands",
        "",
        *[f"- {name}: `{command}`" for name, command in report["commands"].items()],
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    args.markdown_output.write_text("\n".join(lines), encoding="utf-8")
    print("converter_post_layout_candidate_readiness_run")
    print(f"status,{report['status']}")
    print(f"ready_for_strict_submission,{report['ready_for_strict_submission']}")
    print(f"preflight_issue_count,{report['preflight_issue_count']}")
    print(f"json,{args.json_output}")
    print(f"markdown,{args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
