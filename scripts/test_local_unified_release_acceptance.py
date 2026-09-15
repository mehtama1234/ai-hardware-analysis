import json
from pathlib import Path

from check_local_unified_release_acceptance import verify


ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / ".artifacts/local-unified-release-acceptance.json"


def _copy_decision(tmp_path):
    payload = json.loads(DECISION.read_text(encoding="utf-8"))
    output = tmp_path / "decision.json"
    output.write_text(json.dumps(payload), encoding="utf-8")
    return output, payload


def test_current_unified_acceptance_verifies():
    assert verify(DECISION, ROOT) == []


def test_verifier_rejects_tampered_decision(tmp_path):
    path, payload = _copy_decision(tmp_path)
    payload["decision"] = "blocked"
    path.write_text(json.dumps(payload), encoding="utf-8")
    errors = verify(path, ROOT)
    assert "decision digest is invalid" in errors
    assert "decision is not local unified release ready" in errors


def test_verifier_rejects_changed_bound_artifact(tmp_path):
    path, payload = _copy_decision(tmp_path)
    artifact = payload["artifacts"]["model_to_chip_report"]
    artifact["sha256"] = "0" * 64
    path.write_text(json.dumps(payload), encoding="utf-8")
    errors = verify(path, ROOT)
    assert any(error.startswith("artifact digest mismatch:") for error in errors)
