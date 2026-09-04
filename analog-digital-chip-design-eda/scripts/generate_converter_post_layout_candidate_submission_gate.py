#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from generate_converter_post_layout_candidate_progress_gate import ROOT, build_complete_fixture


CURRENT_PAYLOAD = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout" / "payload.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-submission-gate.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-submission-gate.md"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_output_path(stdout: str, key: str) -> Path | None:
    prefix = f"{key},"
    for line in stdout.splitlines():
        if line.startswith(prefix):
            return Path(line[len(prefix):].strip())
    return None


def main() -> None:
    canonical_accepted_dir = ROOT / "evidence" / "aimc-simulator-adapters" / "accepted-post-layout"
    with tempfile.TemporaryDirectory(prefix="candidate-submission-gate-") as tmp:
        tmpdir = Path(tmp)
        _workspace, payload_path, _rerun = build_complete_fixture(tmpdir)
        output_dir = tmpdir / "accepted-output"
        scaffold_run = run([
            sys.executable,
            "scripts/submit_converter_post_layout_payload.py",
            str(CURRENT_PAYLOAD),
            "--expect-reject",
        ])
        complete_run = run([
            sys.executable,
            "scripts/submit_converter_post_layout_payload.py",
            str(payload_path),
            "--output-dir",
            str(output_dir),
        ])
        rerun_path = parse_output_path(complete_run.stdout, "rerun_artifact")
        report_path = parse_output_path(complete_run.stdout, "submission_report")
        rerun = load_json(rerun_path) if rerun_path and rerun_path.exists() else {}
        submission = load_json(report_path) if report_path and report_path.exists() else {}
        temp_output_files = sorted(path.name for path in output_dir.glob("*")) if output_dir.exists() else []

    scaffold_rejected = scaffold_run.returncode == 0 and "PASS converter_post_layout_submission_rejected" in scaffold_run.stdout
    complete_submitted_to_temp = (
        complete_run.returncode == 0
        and "PASS converter_post_layout_submission" in complete_run.stdout
        and submission.get("status") == "accepted_post_layout_payload_rerun_written"
        and rerun.get("result_type") == "converter_post_layout_break_even_rerun"
        and len(temp_output_files) == 2
    )
    no_canonical_accepted_evidence = not canonical_accepted_dir.exists()
    report = {
        "result_type": "converter_post_layout_candidate_submission_gate",
        "status": "submission_gate_passed" if scaffold_rejected and complete_submitted_to_temp and no_canonical_accepted_evidence else "submission_gate_failed",
        "current_scaffold_rejected": scaffold_rejected,
        "temporary_complete_payload_submitted_to_temp_output": complete_submitted_to_temp,
        "canonical_accepted_evidence_persisted": not no_canonical_accepted_evidence,
        "temporary_output_file_count": len(temp_output_files),
        "temporary_output_files": temp_output_files,
        "temporary_replacement_decision": submission.get("replacement_decision"),
        "temporary_claim_ready_to_replace_break_even": submission.get("claim_ready_to_replace_break_even"),
        "claim_boundary": {
            "allowed": "proves strict submission rejects the scaffold and can write temporary accepted-output artifacts for a complete package",
            "not_allowed": "does not write canonical accepted evidence, does not claim the temporary package is real post-layout evidence, and does not prove production readiness",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Candidate Submission Gate",
        "",
        f"- status: `{report['status']}`",
        f"- current scaffold rejected: `{report['current_scaffold_rejected']}`",
        f"- temporary complete payload submitted to temp output: `{report['temporary_complete_payload_submitted_to_temp_output']}`",
        f"- canonical accepted evidence persisted: `{report['canonical_accepted_evidence_persisted']}`",
        f"- temporary output file count: `{report['temporary_output_file_count']}`",
        f"- temporary replacement decision: `{report['temporary_replacement_decision']}`",
        f"- temporary claim ready to replace break-even: `{report['temporary_claim_ready_to_replace_break_even']}`",
        "",
        "This gate runs the strict submission command itself. The current scaffold must be rejected. A complete temporary package must write a rerun artifact and a submission report into a temporary directory. The canonical accepted-evidence directory must remain absent.",
        "",
        "## First Principle",
        "",
        "Submission is where a complete packet starts changing downstream evidence. That means it needs a stronger boundary than preflight. Preflight says the packet can be inspected. Submission says the packet passed strict checks and produced the rerun artifact that later pages may read.",
        "",
        "This gate proves the command path, not the physics. The temporary package is only a shape proof. Real replacement still needs real extracted or measured converter evidence.",
        "",
        "## Temporary Output Files",
        "",
    ]
    if temp_output_files:
        lines.extend(f"- `{name}`" for name in temp_output_files)
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    if report["status"] != "submission_gate_passed":
        raise SystemExit("converter post-layout candidate submission gate failed")
    print("converter_post_layout_candidate_submission_gate")
    print(f"status,{report['status']}")
    print(f"current_scaffold_rejected,{report['current_scaffold_rejected']}")
    print(f"temporary_complete_payload_submitted_to_temp_output,{report['temporary_complete_payload_submitted_to_temp_output']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
