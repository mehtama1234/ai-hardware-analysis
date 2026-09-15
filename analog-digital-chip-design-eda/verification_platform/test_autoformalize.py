import hashlib
import json
from pathlib import Path

import pytest

from verification_platform.autoformalize import AssertionProposal, candidate_from_counterexample, evaluate_proposal_vacuity, evaluate_proposal_vacuity_solver, invoke_assertion_backend, proposal_from_agent_payload, proposal_from_plan, proposal_from_record, refine_assertion_proposal, write_assertion_proposals
from verification_platform.triage import Failure
from verification_platform.ir import Requirement
from verification_platform.planner import plan_requirement


def test_assertion_proposal_binds_sva_to_specification_digest(tmp_path: Path):
    specification = "REQ-COUNTER-HOLD: counter_q holds when enable is low\n"
    spec_digest = hashlib.sha256(specification.encode()).hexdigest()
    proposal = proposal_from_plan(
        plan_requirement(Requirement("REQ-COUNTER-HOLD", "counter_q holds when enable is low")),
        specification_sha256=spec_digest,
        signals=("clk", "rst", "enable", "counter_q"),
        model_id="Qwen/Qwen2.5-0.5B-Instruct",
    )
    proposal.validate(specification_text=specification)
    record = proposal.record()
    assert record["source_kind"] == "specification-grounded"
    assert record["status"] == "review_required"
    assert len(record["proposal_sha256"]) == 64
    path = write_assertion_proposals([proposal], tmp_path / "assertions.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["proposals"][0]["proposal_sha256"] == record["proposal_sha256"]


def test_assertion_proposal_rejects_stale_specification_digest():
    plan = plan_requirement(Requirement("REQ-COUNTER-HOLD", "counter_q holds when enable is low"))
    proposal = proposal_from_plan(plan, specification_sha256="0" * 64, signals=("clk", "rst", "enable", "counter_q"))
    with pytest.raises(ValueError, match="digest does not match"):
        proposal.validate(specification_text="REQ-COUNTER-HOLD: counter_q holds when enable is low\n")


def test_assertion_proposal_rejects_undeclared_functional_identifier():
    from verification_platform.autoformalize import AssertionProposal
    proposal = AssertionProposal("p", "REQ-X", "0" * 64, "assert property (@(posedge clk) secret_state |-> counter_q == 0);", ("clk", "counter_q"), "clk", None)
    with pytest.raises(ValueError, match="undeclared"):
        proposal.validate()


def _proposal():
    specification = "REQ-COUNTER-HOLD: counter_q holds when enable is low\n"
    return proposal_from_plan(
        plan_requirement(Requirement("REQ-COUNTER-HOLD", "counter_q holds when enable is low")),
        specification_sha256=hashlib.sha256(specification.encode()).hexdigest(),
        signals=("clk", "rst", "enable", "counter_q"),
    )


def test_solver_feedback_refines_without_expanding_signal_scope():
    proposal = _proposal()
    refined = refine_assertion_proposal(
        proposal,
        {"proposal_sha256": proposal.proposal_sha256, "status": "counterexample"},
        "assert property (@(posedge clk) disable iff (rst) !enable |=> counter_q == $past(counter_q));",
    )
    assert refined.proposal_id.endswith("-repair-1")
    assert refined.status == "review_required"
    assert set(refined.signals).issubset(set(proposal.signals))


def test_solver_feedback_rejects_stale_or_scope_expanding_repair():
    proposal = _proposal()
    with pytest.raises(ValueError, match="different assertion proposal"):
        refine_assertion_proposal(proposal, {"proposal_sha256": "0" * 64, "status": "counterexample"}, proposal.assertion + " ")
    with pytest.raises(ValueError, match="expand"):
        refine_assertion_proposal(proposal, {"proposal_sha256": proposal.proposal_sha256, "status": "compile_failed"}, "assert property (@(posedge clk) new_signal |-> new_signal);")


def test_vacuity_gate_blocks_unexercised_antecedent(tmp_path: Path):
    proposal = _proposal()
    wave = tmp_path / "trace.vcd"
    wave.write_text("$var wire 1 ! enable $end\n$enddefinitions $end\n#0\n0!\n#5\n0!\n", encoding="utf-8")
    result = evaluate_proposal_vacuity(proposal, wave, antecedent_signal="enable")
    assert result["status"] == "blocked"
    assert result["occurrences"] == 0


def test_vacuity_gate_accepts_active_antecedent_as_only_activity_evidence(tmp_path: Path):
    proposal = _proposal()
    wave = tmp_path / "trace.vcd"
    wave.write_text("$var wire 1 ! enable $end\n$enddefinitions $end\n#0\n0!\n#5\n1!\n", encoding="utf-8")
    result = evaluate_proposal_vacuity(proposal, wave, antecedent_signal="enable")
    assert result["status"] == "active"


def test_solver_vacuity_binds_antecedent_to_proposal_scope(tmp_path: Path):
    source = tmp_path / "dut.sv"
    source.write_text("module dut(input clk, input req, input valid, output q); assign q = req & valid; endmodule\n", encoding="utf-8")
    proposal = AssertionProposal("p1", "REQ-1", "0" * 64, "assert property (@(posedge clk) req |-> valid);", ("clk", "req", "valid"), "clk", None)
    result = evaluate_proposal_vacuity_solver(proposal, source, top="dut", antecedent="req && valid", run_root=tmp_path / "solver", source_revision="v1")
    assert result["status"] == "active"
    blocked = False
    try:
        evaluate_proposal_vacuity_solver(proposal, source, top="dut", antecedent="req && internal_state", run_root=tmp_path / "blocked", source_revision="v1")
    except ValueError:
        blocked = True
    assert blocked
    assert result["solver_status"] == "reachable"
    assert result["evidence"]["claim_boundary"].startswith("bounded reachability")


def test_counterexample_candidate_preserves_declared_scope_and_review_boundary():
    proposal = _proposal()
    candidate = candidate_from_counterexample(proposal, Failure(4, "counter_q", "0", "1"))
    assert candidate.proposal_id.endswith("-cex-1")
    assert "counter_q == 0" in candidate.assertion
    assert candidate.specification_sha256 == proposal.specification_sha256
    assert candidate.status == "review_required"


def test_counterexample_candidate_rejects_unknown_signal_or_literal():
    proposal = _proposal()
    with pytest.raises(ValueError, match="outside"):
        candidate_from_counterexample(proposal, Failure(1, "secret", "0", "1"))
    with pytest.raises(ValueError, match="integer literal"):
        candidate_from_counterexample(proposal, Failure(1, "counter_q", "unknown", "1"))


def test_agent_assertion_payload_is_bound_to_revision_and_structural_scope():
    proposal = proposal_from_agent_payload(
        {"proposal_id": "agent-check", "kind": "check", "source_revision": "rtl-v1", "status": "review_required", "assertion": "assert property (@(posedge clk) disable iff (rst) !enable |=> $stable(counter_q));"},
        requirement_id="REQ-COUNTER-HOLD", specification_sha256="0" * 64,
        structural_signals=("clk", "rst", "enable", "counter_q"), model_id="Qwen/test", source_revision="rtl-v1",
    )
    assert proposal.model_id == "Qwen/test"
    assert set(proposal.signals) == {"clk", "rst", "enable", "counter_q"}


def test_agent_assertion_payload_rejects_scope_expansion():
    with pytest.raises(ValueError, match="expands structural signal scope"):
        proposal_from_agent_payload(
            {"proposal_id": "agent-check", "kind": "check", "source_revision": "rtl-v1", "status": "review_required", "assertion": "assert property (@(posedge clk) secret_state |-> counter_q == 0);"},
            requirement_id="REQ-X", specification_sha256="0" * 64,
            structural_signals=("clk", "counter_q"), model_id="Qwen/test", source_revision="rtl-v1",
        )


def test_agent_assertion_payload_rejects_functional_rtl_context():
    with pytest.raises(ValueError, match="forbidden functional RTL"):
        proposal_from_agent_payload(
            {"proposal_id": "agent-check", "kind": "check", "source_revision": "rtl-v1", "status": "review_required", "context_source": "rtl", "rtl_text": "assign q = buggy_logic;", "assertion": "assert property (@(posedge clk) req |-> ack);"},
            requirement_id="REQ-X", specification_sha256="0" * 64,
            structural_signals=("clk", "req", "ack"), model_id="Qwen/test", source_revision="rtl-v1",
        )


def test_local_backend_assertion_generation_reaches_sva_admission_gate(monkeypatch):
    backend = Path(__file__).parents[1] / "scripts" / "mock_llm_backend.py"
    monkeypatch.setenv("VERIFICATION_LLM_COMMAND", f"python3 {backend}")
    result = invoke_assertion_backend(
        {"task": "generate_assertion", "requirement_id": "REQ-1", "allowed_source_revision": "rtl-v1", "evidence": ["spec://REQ-1"], "assertion": "assert property (@(posedge clk) disable iff (rst) !enable |=> $stable(counter_q));"},
        requirement_id="REQ-1", specification_sha256="0" * 64, structural_signals=("clk", "rst", "enable", "counter_q"),
        model_id="Qwen/test", source_revision="rtl-v1",
    )
    assert result["status"] == "available"
    assert result["proposal"]["status"] == "review_required"


def test_persisted_assertion_record_can_be_rehydrated_for_feedback():
    original = _proposal()
    restored = proposal_from_record(original.record())
    refined = refine_assertion_proposal(
        restored, {"proposal_sha256": restored.proposal_sha256, "status": "vacuous"},
        "assert property (@(posedge clk) disable iff (rst) enable |-> counter_q == $past(counter_q));",
    )
    assert refined.status == "review_required"
    assert refined.specification_sha256 == original.specification_sha256
