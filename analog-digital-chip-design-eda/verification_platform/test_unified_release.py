import json
from pathlib import Path

import pytest

from scripts.build_unified_release_manifest import build
from scripts.verify_unified_release_manifest import verify


ROOT = Path(__file__).resolve().parents[1]


def test_unified_release_preserves_open_physical_claims():
    result = build(
        root=ROOT,
        digital_path=ROOT / "benchmarks/multi_design_pilot/runs/latest/pilot-release-manifest.json",
        mixed_signal_path=ROOT / "evidence/aimc-hardware-lab/verification-platform-mixed-signal-manifest.json",
    )
    assert result["digital"]["reference_release_verified"] is True
    assert result["qualification"]["simulation"] == "proven"
    assert result["qualification"]["physical_layout"] == "unsupported"
    assert result["qualification"]["measured_hardware"] == "unsupported"
    assert result["release_decision"] == "blocked_pending_qualification"
    assert len(result["manifest_sha256"]) == 64


def test_unified_release_rejects_tampered_mixed_signal_evidence(tmp_path: Path):
    source = ROOT / "evidence/aimc-hardware-lab/verification-platform-mixed-signal-manifest.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["artifacts"][0]["evidence"]["sha256"] = "0" * 64
    path = tmp_path / "mixed.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="self-digest does not match"):
        build(root=ROOT, digital_path=ROOT / "benchmarks/multi_design_pilot/runs/latest/pilot-release-manifest.json", mixed_signal_path=path)


def test_unified_release_verifier_accepts_current_artifact():
    path = ROOT / ".artifacts/unified-hardware-verification-release.json"
    assert verify(path, ROOT) == []


def test_unified_release_verifier_rejects_claim_upgrade(tmp_path: Path):
    path = ROOT / ".artifacts/unified-hardware-verification-release.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["qualification"]["physical_layout"] = "proven"
    tampered = tmp_path / "unified.json"
    tampered.write_text(json.dumps(payload), encoding="utf-8")
    assert "unified release self-digest does not match" in verify(tampered, ROOT)


def test_unified_release_verifier_rejects_swapped_parent_manifest(tmp_path: Path):
    path = ROOT / ".artifacts/unified-hardware-verification-release.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["digital"]["manifest_sha256"] = "0" * 64
    payload["manifest_sha256"] = __import__("scripts.build_unified_release_manifest", fromlist=["_digest"])._digest({key: value for key, value in payload.items() if key != "manifest_sha256"})
    tampered = tmp_path / "unified.json"
    tampered.write_text(json.dumps(payload), encoding="utf-8")
    assert "digital parent manifest digest does not match" in verify(tampered, ROOT)
