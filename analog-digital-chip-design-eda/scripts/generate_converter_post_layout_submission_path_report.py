#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from generate_converter_post_layout_positive_path_report import write_positive_fixture


ROOT = Path(__file__).resolve().parents[1]
SUBMIT = ROOT / "scripts" / "submit_converter_post_layout_payload.py"
PLACEHOLDER = ROOT / "evidence" / "aimc-simulator-adapters" / "dry-run" / "converter-post-layout-evidence.placeholder.json"
SHAPE_ONLY = ROOT / "evidence" / "aimc-simulator-adapters" / "dry-run" / "converter-post-layout-evidence.shape-only-missing-files.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-submission-path-report.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-submission-path-report.md"


def run(args: list[str]) -> dict[str, object]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "command": args,
        "returncode": result.returncode,
        "stdout": result.stdout.strip().splitlines(),
        "stderr": result.stderr.strip().splitlines(),
    }


def main() -> None:
    placeholder_rejection = run(["python3", str(SUBMIT), "--expect-reject", str(PLACEHOLDER)])
    missing_file_rejection = run(["python3", str(SUBMIT), "--expect-reject", str(SHAPE_ONLY)])
    with tempfile.TemporaryDirectory(prefix="aimc-post-layout-submit-") as tmp:
        tmp_path = Path(tmp)
        payload_path, _ = write_positive_fixture(tmp_path)
        accepted_dir = tmp_path / "accepted"
        positive_submit = run(["python3", str(SUBMIT), str(payload_path), "--output-dir", str(accepted_dir)])
        accepted_files = sorted(path.name for path in accepted_dir.glob("*.json")) if accepted_dir.exists() else []
    placeholder_rejected = placeholder_rejection["returncode"] == 0 and any("PASS converter_post_layout_submission_rejected" in line for line in placeholder_rejection["stdout"])
    missing_files_rejected = missing_file_rejection["returncode"] == 0 and any("PASS converter_post_layout_submission_rejected" in line for line in missing_file_rejection["stdout"])
    positive_accepted = positive_submit["returncode"] == 0 and any("PASS converter_post_layout_submission" in line for line in positive_submit["stdout"])
    payload = {
        "result_type": "converter_post_layout_submission_path_report",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "submission_path_ready_waiting_for_real_payload" if placeholder_rejected and missing_files_rejected and positive_accepted else "submission_path_failed",
        "submission_script": str(SUBMIT.relative_to(ROOT)),
        "placeholder_rejected": placeholder_rejected,
        "missing_file_payload_rejected": missing_files_rejected,
        "temporary_positive_payload_accepted": positive_accepted,
        "temporary_accepted_files": accepted_files,
        "temporary_fixture_persisted": False,
        "checks": {
            "placeholder_rejection": placeholder_rejection,
            "missing_file_rejection": missing_file_rejection,
            "positive_submit": positive_submit,
        },
        "claim_boundary": {
            "allowed": "proves the one-command submission path rejects bad inputs and writes a rerun artifact for a temporary complete fixture",
            "not_allowed": "does not submit, save, or claim real post-layout converter evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Submission Path",
        "",
        "This report proves the one-command intake path for a future real converter payload.",
        "",
        f"- status: `{payload['status']}`",
        f"- submission script: `{payload['submission_script']}`",
        f"- placeholder rejected: `{payload['placeholder_rejected']}`",
        f"- missing-file payload rejected: `{payload['missing_file_payload_rejected']}`",
        f"- temporary positive payload accepted: `{payload['temporary_positive_payload_accepted']}`",
        f"- temporary fixture persisted: `{payload['temporary_fixture_persisted']}`",
        "",
        "## First-Principles Reading",
        "",
        "Submission is the point where a payload becomes part of the evidence trail. That step should not be a manual copy of files. It should run the same strict checks every time: field validation, file existence, break-even rerun, and a written submission report.",
        "",
        "The dry run proves three things. The placeholder is rejected. A shape-correct payload with missing files is rejected. A temporary complete fixture is accepted and writes rerun/report files only inside a temporary directory. That means the command path is ready without storing synthetic post-layout evidence.",
        "",
        "## Command For A Real Payload",
        "",
        "Run `python3 scripts/submit_converter_post_layout_payload.py REAL_PAYLOAD.json`.",
        "",
        "## Refused Claim",
        "",
        payload["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    if payload["status"] != "submission_path_ready_waiting_for_real_payload":
        raise SystemExit("converter post-layout submission path failed")
    print("converter_post_layout_submission_path")
    print(f"status,{payload['status']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
