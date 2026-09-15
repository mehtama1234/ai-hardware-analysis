#!/usr/bin/env python3
"""Run the complete provider-free customer pilot certification gate."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> str:
    print(f"[certification-gate] {' '.join(command)}", flush=True)
    timeout = 90 if "verify_workbench_browser.py" in command[-1] else (300 if "run_workbench_adversarial_judge.py" in command[-1] else 360)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, timeout=timeout)
    if completed.returncode:
        raise RuntimeError(f"{' '.join(command)} failed ({completed.returncode}): {(completed.stdout + completed.stderr)[-4000:]}")
    return completed.stdout.strip()


def main() -> int:
    python = sys.executable
    run([python, "scripts/run_customer_pilot_certification.py"])
    run([python, "scripts/verify_pilot_scorecard_evidence.py", ".artifacts/customer-pilot-scorecard.json", "--root", "."])
    run([python, "scripts/validate_pilot_scorecard.py", ".artifacts/customer-pilot-scorecard.json"])
    run([python, "-m", "pytest", "-q", "deployment/test_recovery_snapshot.py"])
    # The deterministic browser gate is the bounded CI surface; the heavier
    # handoff walkthrough is retained as a separately captured artifact.
    run([python, "scripts/verify_workbench_browser.py"])
    run([python, "scripts/run_workbench_adversarial_judge.py", "--timeout-seconds", "300"])
    run([python, "scripts/run_production_pilot_flight.py"])
    run([python, "scripts/build_public_reference_archive.py"])
    run([python, "scripts/verify_public_reference_archive.py", ".artifacts/public-reference-release.tar.gz"])
    run([python, "scripts/replay_public_reference_archive.py", ".artifacts/public-reference-release.tar.gz", "--output", ".artifacts/public-reference-replay.json"])
    run([python, "scripts/build_commercial_handoff_manifest.py", "--output", ".artifacts/commercial-handoff-manifest.json"])
    run([python, "scripts/verify_commercial_handoff_manifest.py", ".artifacts/commercial-handoff-manifest.json", "--root", "."])
    run([python, "scripts/build_production_pilot_packet.py"])
    certification = json.loads((ROOT / ".artifacts/customer-pilot-certification.json").read_text(encoding="utf-8"))
    replay = json.loads((ROOT / ".artifacts/public-reference-replay.json").read_text(encoding="utf-8"))
    print(json.dumps({"certification_projects": certification["project_count"], "certified_synthetic_runs": certification["certified_synthetic_runs"], "scorecard_sample_size": certification["scorecard"]["sample_size"], "archive_replay_designs": replay["design_count"], "archive_replay_passed_retests": replay["passed_retests"], "gate": "passed"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
