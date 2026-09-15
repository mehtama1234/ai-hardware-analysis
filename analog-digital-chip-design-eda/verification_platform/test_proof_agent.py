import pytest

from .proof_agent import build_proof_agent_requests, run_proof_agent


def test_proof_agent_requests_are_typed_as_lemma_and_review_roles():
    requests = build_proof_agent_requests(property_id="counter-hold", source_revision="counter-v2", evidence=["formal.log"], failure_context="bounded proof passes but induction is unknown")
    assert [item["role"] for item in requests] == ["invariant_generator", "reviewer"]
    assert requests[0]["allowed_source_revision"] == "counter-v2"


def test_proof_agent_uses_local_fixture_and_persists_review_only_trace(monkeypatch, tmp_path):
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {root / 'scripts/mock_repository_agent_backend.py'}")
    result = run_proof_agent(property_id="counter-hold", source_revision="counter-v2", evidence=["formal.log"], failure_context="bounded proof passes but induction is unknown", backend="local", output_root=tmp_path)
    assert result["team"]["status"] == "available"
    assert result["team"]["results"][0]["proposal"]["kind"] == "lemma"
    assert result["team"]["results"][1]["proposal"]["kind"] == "next_action"
    assert (tmp_path / "proof-agent-run.json").is_file()


def test_proof_agent_rejects_missing_context():
    with pytest.raises(ValueError, match="failure_context"):
        build_proof_agent_requests(property_id="p", source_revision="r", evidence=["e"], failure_context=" ")
