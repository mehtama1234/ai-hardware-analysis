import hashlib
import json
from pathlib import Path

from scripts.verify_pilot_scorecard_evidence import verify


def test_scorecard_evidence_verifier_detects_tampering(tmp_path: Path):
    evidence = tmp_path / "runs" / "summary.json"
    evidence.parent.mkdir()
    evidence.write_text('{"status":"pass"}\n', encoding="utf-8")
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(json.dumps({"evidence_sha256": {"runs/summary.json": digest}}), encoding="utf-8")
    assert verify(scorecard, tmp_path) == []
    evidence.write_text('{"status":"changed"}\n', encoding="utf-8")
    assert verify(scorecard, tmp_path) == ["evidence digest mismatch: runs/summary.json"]


def test_scorecard_evidence_verifier_rejects_unsafe_paths(tmp_path: Path):
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(json.dumps({"evidence_sha256": {"../outside.json": "a" * 64}}), encoding="utf-8")
    assert verify(scorecard, tmp_path) == ["unsafe evidence path: ../outside.json"]
