#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from generate_converter_post_layout_positive_path_report import write_positive_fixture


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "scripts" / "preflight_converter_post_layout_payload.py"
MISSING_FILES = ROOT / "evidence" / "aimc-simulator-adapters" / "dry-run" / "converter-post-layout-evidence.shape-only-missing-files.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-payload-preflight-report.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-payload-preflight-report.md"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="converter-preflight-") as tmp:
        tmpdir = Path(tmp)
        missing_report = tmpdir / "missing-files-preflight.json"
        ready_report = tmpdir / "ready-preflight.json"
        ready_md = tmpdir / "ready-preflight.md"
        positive_payload, _ = write_positive_fixture(tmpdir)

        missing_run = run([
            sys.executable,
            str(PREFLIGHT),
            str(MISSING_FILES),
            "--json-output",
            str(missing_report),
            "--expect-not-ready",
        ])
        ready_run = run([
            sys.executable,
            str(PREFLIGHT),
            str(positive_payload),
            "--json-output",
            str(ready_report),
            "--markdown-output",
            str(ready_md),
            "--expect-ready",
        ])

        missing = load(missing_report) if missing_report.exists() else {}
        ready = load(ready_report) if ready_report.exists() else {}
        accepted_dir = ROOT / "evidence" / "aimc-simulator-adapters" / "accepted-post-layout"
        synthetic_persisted = any(accepted_dir.glob("*synthetic*")) if accepted_dir.exists() else False

    missing_not_ready = missing_run.returncode == 0 and missing.get("status") == "not_ready_for_strict_submission"
    ready_preflight = ready_run.returncode == 0 and ready.get("status") == "ready_for_strict_submission"
    payload = {
        "result_type": "converter_post_layout_payload_preflight_report",
        "status": "preflight_ready" if missing_not_ready and ready_preflight and not synthetic_persisted else "preflight_failed",
        "missing_file_payload_reported_not_ready": missing_not_ready,
        "temporary_complete_payload_reported_ready": ready_preflight,
        "synthetic_accepted_evidence_persisted": synthetic_persisted,
        "preflight_command": "python3 scripts/preflight_converter_post_layout_payload.py REAL_PAYLOAD.json",
        "missing_file_issue_count": missing.get("issue_count"),
        "ready_issue_count": ready.get("issue_count"),
        "claim_boundary": {
            "allowed": "proves preflight can explain not-ready and ready candidate payloads without importing either as accepted evidence",
            "not_allowed": "does not submit real post-layout evidence, does not write accepted evidence, and does not replace converter break-even assumptions",
        },
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Converter Post-Layout Payload Preflight",
        "",
        f"- status: `{payload['status']}`",
        f"- missing-file payload reported not ready: `{payload['missing_file_payload_reported_not_ready']}`",
        f"- temporary complete payload reported ready: `{payload['temporary_complete_payload_reported_ready']}`",
        f"- synthetic accepted evidence persisted: `{payload['synthetic_accepted_evidence_persisted']}`",
        f"- preflight command: `{payload['preflight_command']}`",
        "",
        "Preflight is the review step before submission. It reads a candidate payload, checks the same shape and file boundaries as strict submission, and writes a report. It does not write accepted evidence.",
        "",
        "## First Principle",
        "",
        "A payload can fail in two different ways. A shape mistake means it does not say enough, such as missing an energy term or using the wrong sharing rule. A file mistake means it says the right kind of thing but points to files that are not present. The second case is dangerous because the payload looks complete while the physical evidence is not inspectable.",
        "",
        "Preflight separates those cases before the final submission command is allowed to touch the accepted evidence directory.",
        "",
        "## Refused Claim",
        "",
        payload["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    if payload["status"] != "preflight_ready":
        raise SystemExit("converter post-layout payload preflight failed")
    print("converter_post_layout_payload_preflight")
    print(f"status,{payload['status']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
