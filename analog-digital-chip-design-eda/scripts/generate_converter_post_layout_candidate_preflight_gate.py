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
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-preflight-gate.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-preflight-gate.md"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    accepted_dir = ROOT / "evidence" / "aimc-simulator-adapters" / "accepted-post-layout"
    with tempfile.TemporaryDirectory(prefix="candidate-preflight-gate-") as tmp:
        tmpdir = Path(tmp)
        workspace, payload_path, _rerun = build_complete_fixture(tmpdir)
        scaffold_report = tmpdir / "scaffold-preflight.json"
        scaffold_md = tmpdir / "scaffold-preflight.md"
        complete_report = tmpdir / "complete-preflight.json"
        complete_md = tmpdir / "complete-preflight.md"
        scaffold_run = run([
            sys.executable,
            "scripts/preflight_converter_post_layout_payload.py",
            str(CURRENT_PAYLOAD),
            "--json-output",
            str(scaffold_report),
            "--markdown-output",
            str(scaffold_md),
            "--expect-not-ready",
        ])
        complete_run = run([
            sys.executable,
            "scripts/preflight_converter_post_layout_payload.py",
            str(payload_path),
            "--json-output",
            str(complete_report),
            "--markdown-output",
            str(complete_md),
            "--expect-ready",
        ])
        scaffold = load_json(scaffold_report) if scaffold_report.exists() else {}
        complete = load_json(complete_report) if complete_report.exists() else {}

    scaffold_rejected = (
        scaffold_run.returncode == 0
        and scaffold.get("status") == "not_ready_for_strict_submission"
        and scaffold.get("shape_validation_passed") is False
        and scaffold.get("referenced_file_validation_passed") is False
        and scaffold.get("same_run_validation_passed") is False
    )
    complete_ready = (
        complete_run.returncode == 0
        and complete.get("status") == "ready_for_strict_submission"
        and complete.get("shape_validation_passed") is True
        and complete.get("referenced_file_validation_passed") is True
        and complete.get("same_run_validation_passed") is True
        and int(complete.get("issue_count", -1)) == 0
    )
    no_accepted_evidence = not accepted_dir.exists()
    report = {
        "result_type": "converter_post_layout_candidate_preflight_gate",
        "status": "preflight_gate_passed" if scaffold_rejected and complete_ready and no_accepted_evidence else "preflight_gate_failed",
        "current_scaffold_rejected": scaffold_rejected,
        "temporary_complete_payload_ready": complete_ready,
        "synthetic_accepted_evidence_persisted": not no_accepted_evidence,
        "current_scaffold_status": scaffold.get("status"),
        "current_scaffold_issue_count": scaffold.get("issue_count"),
        "current_scaffold_same_run_validation_passed": scaffold.get("same_run_validation_passed"),
        "temporary_complete_status": complete.get("status"),
        "temporary_complete_issue_count": complete.get("issue_count"),
        "temporary_complete_same_run_validation_passed": complete.get("same_run_validation_passed"),
        "claim_boundary": {
            "allowed": "proves preflight rejects the current scaffold and accepts a complete temporary package without submission",
            "not_allowed": "does not submit the temporary package, does not write accepted evidence, and does not prove real post-layout physics",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Candidate Preflight Gate",
        "",
        f"- status: `{report['status']}`",
        f"- current scaffold rejected: `{report['current_scaffold_rejected']}`",
        f"- temporary complete payload ready: `{report['temporary_complete_payload_ready']}`",
        f"- synthetic accepted evidence persisted: `{report['synthetic_accepted_evidence_persisted']}`",
        f"- current scaffold issue count: `{report['current_scaffold_issue_count']}`",
        f"- current scaffold same-run validation passed: `{report['current_scaffold_same_run_validation_passed']}`",
        f"- temporary complete issue count: `{report['temporary_complete_issue_count']}`",
        f"- temporary complete same-run validation passed: `{report['temporary_complete_same_run_validation_passed']}`",
        "",
        "This gate runs the actual preflight command against two packages. The current candidate scaffold must be rejected. A temporary complete package must be ready. Neither path is allowed to write accepted evidence.",
        "",
        "## First Principle",
        "",
        "Preflight is the door before submission. It should answer one narrow question: can the package be inspected enough for strict submission to start? If fields are placeholders or files are missing, the answer is no. If the fields are concrete and the files exist, the answer is yes.",
        "",
        "This still does not say the converter is good. It says the packet is complete enough to be judged.",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    if report["status"] != "preflight_gate_passed":
        raise SystemExit("converter post-layout candidate preflight gate failed")
    print("converter_post_layout_candidate_preflight_gate")
    print(f"status,{report['status']}")
    print(f"current_scaffold_rejected,{report['current_scaffold_rejected']}")
    print(f"temporary_complete_payload_ready,{report['temporary_complete_payload_ready']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
