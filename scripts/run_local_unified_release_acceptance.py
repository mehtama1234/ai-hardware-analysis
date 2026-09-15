#!/usr/bin/env python3
"""Run the provider-free digital and model-to-chip release acceptance paths."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
EDA = ROOT / "analog-digital-chip-design-eda"
ARTIFACTS = ROOT / ".artifacts"


def run(label: str, command: list[str], cwd: Path) -> dict:
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    return {"label": label, "cwd": str(cwd), "command": command,
            "returncode": completed.returncode, "stdout": completed.stdout[-12000:],
            "stderr": completed.stderr[-12000:]}


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ARTIFACTS / "local-unified-release-acceptance.json")
    parser.add_argument("--skip-adversarial", action="store_true", help="skip the local browser/API adversarial gate")
    args = parser.parse_args()
    python = sys.executable
    public_command = [python, "scripts/run_public_reference_acceptance.py"]
    if args.skip_adversarial:
        public_command.append("--skip-adversarial")
    steps = [
        run("customer_pilot_certification", [python, "scripts/run_customer_pilot_certification_gate.py"], EDA),
        run("public_reference_acceptance", public_command, EDA),
        run("model_to_chip_acceptance", [python, "scripts/run_local_end_to_end_qualification.py"], ROOT),
        run("profile_family_acceptance", [python, "scripts/run_local_profile_family_acceptance.py"], ROOT),
        run("final_gate_report", [python, "scripts/report_end_to_end_status.py"], ROOT),
        run("final_handoff_validation", [python, "scripts/validate_end_to_end_handoff.py"], ROOT),
    ]
    public_source = EDA / ".artifacts/public-reference-acceptance.json"
    public_durable = ARTIFACTS / "public-reference-acceptance.json"
    if public_source.is_file():
        public_durable.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(public_source, public_durable)
    passed = {step["label"] for step in steps if step["returncode"] == 0}
    required = {step["label"] for step in steps}
    decision = {
        "schema_version": "local-unified-release-acceptance-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "backend_policy": "open-source-and-local-cpu-only",
        "hardware_required": False,
        "decision": "local_unified_reference_and_model_to_chip_package_ready_for_signoff" if required <= passed else "blocked",
        "blockers": sorted(required - passed),
        "claim_boundary": "This joins reproducible digital verification with bounded local transformer/profile/fallback evidence. It does not authorize analog execution or claim GPU performance, measured energy, silicon yield, or physical qualification.",
        "steps": steps,
        "artifacts": {},
    }
    artifact_paths = {
        # Keep the acceptance package replayable from a clean checkout; the
        # EDA subrepository intentionally ignores its local .artifacts tree.
        "public_reference_acceptance": ARTIFACTS / "public-reference-acceptance.json",
        "model_to_chip_manifest": ROOT / "evidence/end-to-end-qualification-manifest.json",
        "model_to_chip_report": ROOT / "analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification/local-profile-to-workload-qualification/qualification_report.json",
        "model_to_chip_decision": ROOT / "analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification/local-profile-to-workload-qualification/decision_audit.json",
        "profile_family_manifest": ROOT / "analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification/local-profile-family-replay/manifest.json",
    }
    decision["artifacts"] = {name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                              for name, path in artifact_paths.items()}
    body = json.dumps(decision, sort_keys=True, separators=(",", ":"))
    decision["decision_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision["decision"], "blockers": decision["blockers"], "output": str(args.output)}, sort_keys=True))
    return 0 if decision["decision"] != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
