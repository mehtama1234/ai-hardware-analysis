#!/usr/bin/env python3
"""Run the provider-free public reference release acceptance contract."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / ".artifacts"
PILOT_ROOT = ROOT / "benchmarks" / "multi_design_pilot" / "runs" / "latest"


def run(label: str, command: list[str]) -> dict:
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    return {
        "label": label,
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout[-12000:],
        "stderr": completed.stderr[-12000:],
    }


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ARTIFACTS / "public-reference-acceptance.json")
    parser.add_argument("--skip-adversarial", action="store_true", help="skip the browser/service adversarial gate")
    args = parser.parse_args()
    python = sys.executable
    steps = [
        run("multi_design_pilot", [python, "benchmarks/multi_design_pilot/ci_gate.py"]),
        run("build_scorecard", [python, "scripts/build_open_source_pilot_scorecard.py", str(PILOT_ROOT), ".artifacts/open-source-pilot-scorecard.json"]),
        run("verify_scorecard", [python, "scripts/verify_pilot_scorecard_evidence.py", ".artifacts/open-source-pilot-scorecard.json", "--root", "."]),
        run("build_archive", [python, "scripts/build_public_reference_archive.py", "--output", ".artifacts/public-reference-release.tar.gz"]),
        run("verify_archive", [python, "scripts/verify_public_reference_archive.py", ".artifacts/public-reference-release.tar.gz"]),
        run("replay_archive", [python, "scripts/replay_public_reference_archive.py", ".artifacts/public-reference-release.tar.gz"]),
    ]
    if not args.skip_adversarial:
        steps.append(run("adversarial_browser_service", [python, "scripts/run_workbench_adversarial_judge.py"]))

    scorecard = ARTIFACTS / "open-source-pilot-scorecard.json"
    archive = ARTIFACTS / "public-reference-release.tar.gz"
    decision = {
        "schema_version": "public-reference-acceptance-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "backend_policy": "open-source-only",
        "hardware_required": False,
        "claim_boundary": "Provider-free reference release only; this does not establish formal completeness, silicon correctness, physical AIMC qualification, measured hardware, customer ROI, or production readiness.",
        "steps": steps,
        "artifacts": {
            "scorecard": {"path": str(scorecard.relative_to(ROOT)), "sha256": digest(scorecard)},
            "archive": {"path": str(archive.relative_to(ROOT)), "sha256": digest(archive)},
            "pilot_summary": {"path": str(PILOT_ROOT / "pilot-summary.json"), "sha256": digest(PILOT_ROOT / "pilot-summary.json")},
            "closure_decision": {"path": ".artifacts/closure-lab-decision.json", "sha256": digest(ARTIFACTS / "closure-lab-decision.json")},
        },
    }
    required = {"multi_design_pilot", "build_scorecard", "verify_scorecard", "build_archive", "verify_archive", "replay_archive"}
    if not args.skip_adversarial:
        required.add("adversarial_browser_service")
    passed_labels = {step["label"] for step in steps if step["returncode"] == 0}
    decision["decision"] = "public_reference_release_ready_for_human_signoff" if required <= passed_labels else "blocked"
    decision["blockers"] = sorted(required - passed_labels)
    body = json.dumps(decision, sort_keys=True, separators=(",", ":"))
    decision["decision_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision["decision"], "blockers": decision["blockers"], "output": str(args.output)}, sort_keys=True))
    return 0 if decision["decision"] != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
