from pathlib import Path

from verification_platform.agent_team import run_agent_team
from verification_platform.agent import AgentProposal
from verification_platform.llm_backend import BackendResult


def test_agent_team_passes_bounded_role_handoffs(monkeypatch):
    backend = Path(__file__).parents[1] / "scripts" / "mock_llm_backend.py"
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {backend}")
    evidence = ["collateral/package.json", "debug/package.json"]
    result = run_agent_team([
        {"role": "diagnostician", "task": "diagnose_failure", "allowed_source_revision": "team-v1", "evidence": evidence, "failure": {"signal": "q", "cycle": 2, "expected": "0", "actual": "1"}},
        {"role": "repair_proposer", "task": "propose_repair", "allowed_source_revision": "team-v1", "evidence": evidence, "failure": {"signal": "q", "cycle": 2, "expected": "0", "actual": "1"}, "repair_operator_choices": ["approval_gated_copy_only"]},
        {"role": "assertion_generator", "task": "generate_assertion", "allowed_source_revision": "team-v1", "evidence": evidence, "requirement_id": "REQ-Q", "assertion": "assert property (@(posedge clk) req |-> ack);"},
    ], backend="local", source_revision="team-v1")
    assert result["status"] == "available"
    assert len(result["handoffs"]) == 3
    assert result["results"][1]["proposal"]["kind"] == "repair"
    assert result["results"][2]["proposal"]["kind"] == "check"
    assert all(item["grounded"] for item in result["results"])


def test_agent_team_blocks_wrong_role_or_untrusted_evidence(monkeypatch):
    backend = Path(__file__).parents[1] / "scripts" / "mock_llm_backend.py"
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {backend}")
    result = run_agent_team([
        {"role": "repair_proposer", "task": "diagnose_failure", "allowed_source_revision": "team-v2", "evidence": ["evidence"]},
        {"role": "diagnostician", "task": "diagnose_failure", "allowed_source_revision": "old", "evidence": ["evidence"], "failure": {"signal": "q", "cycle": 1, "expected": "0", "actual": "1"}},
    ], backend="local", source_revision="team-v2")
    assert result["status"] == "blocked"
    assert all(item["status"] == "blocked" for item in result["results"])


def test_agent_team_blocks_wrong_exact_repair_choice(monkeypatch):
    proposal = AgentProposal(
        proposal_id="wrong-repair", kind="repair", source_revision="team-v3",
        action="apply bounded edit", rationale="review required", evidence=("failure.log",), status="review_required",
    )
    monkeypatch.setattr(
        "verification_platform.agent_team.invoke_local_backend",
        lambda request: BackendResult("test", "available", proposal=proposal, raw={"before": "wrong", "after": "new"}),
    )
    result = run_agent_team([
        {"role": "repair_proposer", "task": "propose repair", "allowed_source_revision": "team-v3", "evidence": ["failure.log"], "repair_before": "old", "repair_after": "new"},
    ], backend="local", source_revision="team-v3")
    assert result["status"] == "blocked"
    assert result["results"][0]["status"] == "blocked"
    assert "repair-choice" in result["results"][0]["error"]
