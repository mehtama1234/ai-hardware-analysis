import json
import pytest
import subprocess
import sys

from scripts.run_workbench_adversarial_judge import main, packet_digest, run_bounded, validate_findings


def _finding(**overrides):
    value = {
        "severity": "P2", "role": "debug", "action_sequence": ["select a run"],
        "expected": "e", "observed": "o", "evidence": ["trace.json"],
        "trust_risk": "r", "acceptance_test": "a",
    }
    value.update(overrides)
    return value


def test_validate_findings_accepts_documented_shape():
    assert validate_findings([_finding()])[0]["severity"] == "P2"


def test_packet_digest_is_canonical_and_excludes_digest_field():
    packet = {"schema": "v1", "findings": [], "packet_sha256": "stale"}
    digest = packet_digest(packet)
    packet["packet_sha256"] = digest
    assert packet_digest(packet) == digest
    packet["findings"].append({"id": "new"})
    assert packet_digest(packet) != digest


def test_empty_attached_findings_file_remains_auditable(tmp_path, monkeypatch):
    findings = tmp_path / "findings.json"
    findings.write_text("[]\n", encoding="utf-8")
    output = tmp_path / "packet.json"
    monkeypatch.setattr(sys, "argv", ["judge", "--findings", str(findings), "--output", str(output)])
    monkeypatch.setattr(sys, "executable", "python3")
    monkeypatch.setattr("scripts.run_workbench_adversarial_judge.run_bounded", lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, "gate ok", ""))
    assert main() == 0
    packet = json.loads(output.read_text(encoding="utf-8"))
    assert packet["adjudication_status"] == "findings_attached_for_reproduction"
    assert packet["llm_adjudication"]["finding_count"] == 0


@pytest.mark.parametrize("bad", [
    [_finding(severity="P9")],
    [_finding(role="operator")],
    [_finding(evidence="trace.json")],
    [_finding(action_sequence="select a run")],
    [_finding(evidence=[])],
    [_finding(expected="")],
    [_finding(evidence=["trace.json", 4])],
    [{"severity": "P2"}],
])
def test_validate_findings_rejects_malformed_model_output(bad):
    with pytest.raises(ValueError):
        validate_findings(bad)


def test_bounded_gate_returns_terminal_timeout_result(monkeypatch, tmp_path):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"], output=b"partial")
    monkeypatch.setattr(subprocess, "run", timeout)
    result = run_bounded(["tool"], cwd=tmp_path, env={}, timeout_seconds=1)
    assert result.returncode == 124
    assert "TIMEOUT" in result.stderr
