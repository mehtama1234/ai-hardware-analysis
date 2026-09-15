"""Run the deterministic adversarial preflight and emit an LLM-judge packet.

The packet deliberately separates observed browser evidence from any later LLM
interpretation. It can be supplied to a skeptical model together with the
screenshots and API traces produced by the workbench checks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCENARIOS = [
    ("selection_isolation", "debug", "Select two runs and verify the second has only its own evidence."),
    ("project_switch_isolation", "debug", "Switch projects after review and verify prior state is cleared."),
    ("missing_waveform", "debug", "A run without a waveform must say evidence is unavailable."),
    ("repair_digest", "lead", "A changed repair proposal digest must be rejected before retest."),
    ("narrow_retest", "lead", "A narrower retest must remain incomparable rather than auto-closing."),
    ("credential_boundary", "first-time", "Invalid credentials must not expose sample metrics in live mode."),
    ("coverage_boundary", "lead", "A missing coverage marker must remain unreported."),
    ("disconnect_recovery", "first-time", "A disconnected service must preserve identity and offer recovery without fabricating fresh evidence."),
]


def run_bounded(command: list[str], *, cwd: Path, env: dict[str, str], timeout_seconds: float) -> subprocess.CompletedProcess[str]:
    """Run one deterministic gate with a terminal, serializable timeout result."""
    try:
        return subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout.decode(errors="replace") if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode(errors="replace") if isinstance(error.stderr, bytes) else (error.stderr or "")
        return subprocess.CompletedProcess(command, 124, stdout=stdout, stderr=stderr + "\nTIMEOUT\n")

def validate_findings(supplied):
    findings = supplied.get("findings", []) if isinstance(supplied, dict) else supplied
    if not isinstance(findings, list):
        raise ValueError("findings must be a JSON array or an object with a findings array")
    allowed_severity = {"P0", "P1", "P2", "P3"}; allowed_roles = {"first-time", "debug", "lead"}
    required = {"severity", "role", "action_sequence", "expected", "observed", "evidence", "trust_risk", "acceptance_test"}
    for finding in findings:
        if not isinstance(finding, dict) or not required.issubset(finding) or finding["severity"] not in allowed_severity or finding["role"] not in allowed_roles:
            raise ValueError("each finding must match the documented adversarial finding schema")
        if (not isinstance(finding["action_sequence"], list) or not finding["action_sequence"]
                or not isinstance(finding["evidence"], list) or not finding["evidence"]):
            raise ValueError("finding action_sequence and evidence must be non-empty arrays")
        if any(not isinstance(item, str) or not item.strip() for item in finding["action_sequence"] + finding["evidence"]):
            raise ValueError("finding action_sequence and evidence entries must be non-empty strings")
        for field in ("expected", "observed", "trust_risk", "acceptance_test"):
            if not isinstance(finding[field], str) or not finding[field].strip():
                raise ValueError(f"finding {field} must be a non-empty string")
    return findings


def packet_digest(packet: dict) -> str:
    """Return the canonical digest for a packet before its digest field."""
    payload = {key: value for key, value in packet.items() if key != "packet_sha256"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / ".artifacts" / "workbench-adversarial" / "judge-packet.json"))
    parser.add_argument("--findings", help="JSON array or object containing LLM-produced findings to validate and attach")
    parser.add_argument("--timeout-seconds", type=float, default=180.0, help="Maximum time for each deterministic browser/service gate")
    args = parser.parse_args()
    chromium = os.environ.get("WORKBENCH_CHROMIUM")
    command = ["python3", str(ROOT / "scripts" / "verify_workbench_browser.py")]
    env = os.environ.copy()
    if chromium:
        env["WORKBENCH_CHROMIUM"] = chromium
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    completed = run_bounded(command, cwd=ROOT, env=env, timeout_seconds=args.timeout_seconds)
    service_command = ["python3", "-m", "pytest", "deployment/test_workbench_repair_e2e.py", "deployment/test_workbench_execution_e2e.py", "-q"]
    service_check = run_bounded(service_command, cwd=ROOT, env=env, timeout_seconds=args.timeout_seconds)
    observed = completed.stdout + ("\n" + completed.stderr if completed.stderr else "")
    service_observed = service_check.stdout + ("\n" + service_check.stderr if service_check.stderr else "")
    passed = completed.returncode == 0 and service_check.returncode == 0
    findings = []
    findings_attached = False
    findings_metadata = {
        "status": "not_attached",
        "claim_boundary": "No independent LLM adjudication is present; deterministic gate results remain separate.",
    }
    if args.findings:
        findings_attached = True
        findings_path = Path(args.findings)
        findings_bytes = findings_path.read_bytes()
        findings = validate_findings(json.loads(findings_bytes.decode("utf-8")))
        findings_metadata = {
            "status": "attached_for_reproduction",
            "source": str(findings_path),
            "source_sha256": hashlib.sha256(findings_bytes).hexdigest(),
            "finding_count": len(findings),
            "claim_boundary": "LLM findings are hypotheses until reproduced by the deterministic suite; diagnosis correctness and usability remain separate.",
        }
    packet = {
        "schema": "verification-workbench.adversarial-judge.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "judge_type": "deterministic_plus_llm_input" if findings_attached else "deterministic_preflight",
        "adjudication_status": "findings_attached_for_reproduction" if findings_attached else "awaiting_external_llm_adjudication",
        "llm_adjudication": findings_metadata,
        "llm_instruction": "Treat each scenario as a hypothesis. Report only findings supported by the attached browser/API evidence; separate diagnosis correctness from usability.",
        "judge_prompt": "Review the attached screenshots, DOM/API traces, and action output as a skeptical semiconductor verification engineer. For each scenario, report only reproducible UX or trust failures using the finding schema in docs/evaluations/verification-workbench-adversarial-judge.md. Do not infer live evidence from sample data, and do not award credit for prose that conflicts with an artifact.",
        "source_command": [" ".join(command), " ".join(service_command)],
        "deterministic_gate": {"passed": passed, "browser": {"returncode": completed.returncode, "output": observed[-12000:]}, "service": {"returncode": service_check.returncode, "output": service_observed[-12000:]}},
        "scenarios": [
            {"id": scenario, "role": role, "action_sequence": [action], "status": "covered_by_gate" if passed else "gate_failed", "evidence_required": "browser/API artifact plus finding reproduction"}
            for scenario, role, action in SCENARIOS
        ],
        "findings": findings,
        "evidence": [
            str(ROOT / ".artifacts" / "workbench-browser" / "live-unavailable.png"),
            str(ROOT / "docs" / "evaluations" / "verification-workbench-adversarial-judge.md"),
        ],
    }
    packet["packet_sha256"] = packet_digest(packet)
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "gate_passed": passed, "scenarios": len(SCENARIOS)}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
