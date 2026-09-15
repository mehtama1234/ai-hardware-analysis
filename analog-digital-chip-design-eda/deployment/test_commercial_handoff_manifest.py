import json
from pathlib import Path

from scripts.build_commercial_handoff_manifest import build_manifest
from scripts.verify_commercial_handoff_manifest import verify, verify_adversarial_packet


def test_handoff_manifest_hashes_required_artifacts(tmp_path: Path, monkeypatch):
    # Use a minimal copy of the required paths to keep the contract test fast.
    import scripts.build_commercial_handoff_manifest as module
    monkeypatch.setattr(module, "ARTIFACTS", ("a.txt",))
    (tmp_path / "a.txt").write_text("evidence\n", encoding="utf-8")
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps({"customer_production_ready": False}), encoding="utf-8")
    manifest = build_manifest(tmp_path, readiness=readiness)
    assert manifest["schema_version"] == "verification-commercial-handoff-v1"
    assert manifest["artifact_count"] == 2
    assert manifest["customer_production_ready"] is False
    assert len(manifest["artifacts"]["a.txt"]["sha256"]) == 64
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert verify(manifest_path, tmp_path) == []
    manifest["artifact_count"] = 99
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert verify(manifest_path, tmp_path) == ["manifest_sha256 does not match manifest content"]


def test_adversarial_packet_self_digest_is_verified(tmp_path: Path):
    from scripts.run_workbench_adversarial_judge import packet_digest
    scenarios = ["selection_isolation", "project_switch_isolation", "missing_waveform", "repair_digest", "narrow_retest", "credential_boundary", "coverage_boundary", "disconnect_recovery"]
    packet = {"schema": "v1", "deterministic_gate": {"passed": True}, "scenarios": [{"id": item} for item in scenarios]}
    packet["packet_sha256"] = packet_digest(packet)
    path = tmp_path / "judge-packet.json"
    path.write_text(json.dumps(packet), encoding="utf-8")
    assert verify_adversarial_packet(path) == []
    packet["deterministic_gate"]["passed"] = False
    path.write_text(json.dumps(packet), encoding="utf-8")
    assert verify_adversarial_packet(path) == [
        "packet_sha256 does not match packet content",
        "deterministic adversarial gate is not passed",
    ]
