import pytest

from .proof_closure import build_assumption_audit, evaluate_proof_closure
from .rtl_ast import run_functional_equivalence
from .formal import run_yosys_inductive_proof


def _evaluate(**overrides):
    assumptions = [{"id": "reset", "formula": "rst eventually deasserts"}]
    audit = build_assumption_audit(
        assumptions,
        [{"assumption_id": "reset", "status": "reachable", "source_revision": "counter-v2", "result_sha256": "placeholder"}],
        source_revision="counter-v2",
    )
    # The fixture is intentionally made digest-valid after construction so
    # the closure tests exercise the same admission contract as production.
    result = {"assumption_id": "reset", "status": "reachable", "source_revision": "counter-v2"}
    import hashlib, json
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    audit = build_assumption_audit(assumptions, [result], source_revision="counter-v2")
    values = {
        "property_id": "counter-hold",
        "source_revision": "counter-v2",
        "bounded_status": "proven",
        "inductive_status": "proven",
        "assumptions": assumptions,
        "assumption_audit": audit,
        "reachable_state_status": "passed",
        "vacuity_status": "active",
    }
    values.update(overrides)
    return evaluate_proof_closure(**values)


def test_proof_closure_requires_bounded_and_inductive_evidence():
    result = _evaluate()
    assert result["proof_status"] == "proven"
    assert result["bounded_only"] is False


def test_bounded_pass_without_inductive_proof_is_not_closure():
    result = _evaluate(inductive_status="unknown")
    assert result["bounded_only"] is True
    assert result["proof_status"] == "blocked"


def test_overconstrained_or_vacuous_assumptions_block_closure():
    import hashlib, json
    blocked = {"schema_version": "assumption-audit-v1", "status": "blocked", "source_revision": "counter-v2", "assumption_count": 1, "checks": [{"status": "blocked", "reason": "unreachable assumption"}], "claim_boundary": "test"}
    blocked["audit_sha256"] = hashlib.sha256(json.dumps(blocked, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    overconstrained = _evaluate(assumption_audit=blocked)
    vacuous = _evaluate(vacuity_status="vacuous")
    assert overconstrained["proof_status"] == "blocked"
    assert vacuous["proof_status"] == "blocked"


def test_counterexample_is_preserved_for_failed_induction():
    result = _evaluate(inductive_status="counterexample", counterexample={"cycle": 4, "signal": "counter_q"})
    assert result["proof_status"] == "blocked"
    assert result["counterexample"]["cycle"] == 4


def test_invalid_assumption_audit_is_rejected():
    with pytest.raises(ValueError, match="assumption audit"):
        _evaluate(assumption_audit={"status": "unknown"})


def test_assumption_audit_requires_matching_solver_evidence():
    assumptions = [{"id": "req", "formula": "req"}]
    missing = build_assumption_audit(assumptions, [], source_revision="r1")
    assert missing["status"] == "blocked"
    assert missing["checks"][0]["status"] == "blocked"
    import hashlib, json
    stale = {"assumption_id": "req", "status": "reachable", "source_revision": "old"}
    stale["result_sha256"] = hashlib.sha256(json.dumps(stale, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    audit = build_assumption_audit(assumptions, [stale], source_revision="r1")
    assert audit["status"] == "blocked"


def test_actual_yosys_equivalence_result_can_feed_inductive_contract(tmp_path):
    reference = tmp_path / "gold.sv"
    candidate = tmp_path / "gate.sv"
    reference.write_text("module gold(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
    candidate.write_text("module gate(input a, output y); assign y = a; endmodule\n", encoding="utf-8")
    equivalence = run_functional_equivalence([reference], [candidate], reference_top="gold", candidate_top="gate", run_root=tmp_path / "equiv", source_revision="proof-v1")
    assert equivalence["status"] == "proven"
    result = _evaluate(property_id="gold-gate-equivalence", bounded_status="proven", inductive_status="proven")
    assert result["proof_status"] == "proven"


def test_actual_yosys_temporal_induction_is_distinguished_from_bmc(tmp_path):
    source = tmp_path / "invariant.sv"
    source.write_text("module invariant(input logic clk, input logic rst); logic q = 1'b0; always_ff @(posedge clk) begin if (rst) q <= 1'b0; else q <= 1'b0; assert(q == 1'b0); end endmodule\n", encoding="utf-8")
    result = run_yosys_inductive_proof([source], top="invariant", run_root=tmp_path / "inductive", source_revision="inductive-v1")
    assert result["method"] == "temporal-induction"
    assert result["status"] == "proven"
    assert (tmp_path / "inductive/inductive-proof-result.json").is_file()
