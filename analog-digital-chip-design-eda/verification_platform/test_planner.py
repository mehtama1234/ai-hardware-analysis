from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.ir import Requirement, VerificationIR
from verification_platform.planner import plan_ir, plan_requirement, planning_summary


def test_planner_maps_known_requirement_to_traceable_sva():
    plan = plan_requirement(Requirement("REQ-COUNTER-HOLD", "counter_q holds when enable is low"))
    assert plan.id == "CHECK-REQ-COUNTER-HOLD"
    assert "!enable" in plan.assertion
    assert plan.requirement_id == "REQ-COUNTER-HOLD"


def test_planner_does_not_guess_unknown_requirements():
    ir = VerificationIR(requirements=[Requirement("REQ-X", "latency is acceptable")])
    assert plan_ir(ir) == []


def test_planning_summary_identifies_human_review_queue():
    ir = VerificationIR(requirements=[Requirement("REQ-RESET", "counter is reset to zero"), Requirement("REQ-UNKNOWN", "latency is acceptable")])
    summary = planning_summary(ir)
    assert summary["planned"] == ["REQ-RESET"]
    assert summary["unplanned"][0]["requirement_id"] == "REQ-UNKNOWN"


def test_planner_supports_fifo_and_register_contracts():
    fifo = plan_ir(VerificationIR(requirements=[
        Requirement("REQ-FIFO-RESET", "count is zero while rst is asserted"),
        Requirement("REQ-FIFO-BOUNDS", "count never exceeds the FIFO depth"),
        Requirement("REQ-FIFO-WRITE", "a write increments count only when the FIFO is not full"),
    ]))
    reg = plan_ir(VerificationIR(requirements=[
        Requirement("REQ-REG-ADDRESS", "a write to a nonzero address does not change reg0"),
        Requirement("REQ-REG-WRITE", "a write to address zero stores wdata in reg0"),
    ]))
    assert {item.requirement_id for item in fifo} == {"REQ-FIFO-RESET", "REQ-FIFO-BOUNDS", "REQ-FIFO-WRITE"}
    assert {item.requirement_id for item in reg} == {"REQ-REG-ADDRESS", "REQ-REG-WRITE"}

def test_planner_preserves_handshake_signal_identity():
    plan = plan_requirement(Requirement("REQ-CSR-READY", "ready is zero while rst is asserted"))
    assert "ready == '0" in plan.assertion


def test_planner_extracts_generic_signal_and_control_identifiers():
    plans = plan_ir(VerificationIR(requirements=[
        Requirement("REQ-GENERIC-HOLD", "state_q holds its previous value when gate is low"),
        Requirement("REQ-GENERIC-INCR", "level_q increments by one only when valid is high"),
        Requirement("REQ-GENERIC-RESET", "status_q is zero while reset_n is asserted"),
    ]))
    assert len(plans) == 3
    assert "state_q" in plans[0].assertion and "!gate" in plans[0].assertion
    assert "level_q" in plans[1].assertion and "valid" in plans[1].assertion
    assert "reset_n |-> status_q == '0" in plans[2].assertion


def test_planner_supports_explicit_same_and_next_cycle_implications():
    plans = plan_ir(VerificationIR(requirements=[
        Requirement("REQ-VALID-READY", "valid implies ready"),
        Requirement("REQ-REQ-ACK", "req is high and then ack is high on the next cycle"),
    ]))
    assert "valid |-> ready" in plans[0].assertion
    assert "req |=> ack" in plans[1].assertion


def test_planner_supports_bounded_fixed_cycle_response():
    plan = plan_requirement(Requirement("REQ-REQ-ACK-3", "req is high and ack is high 3 cycles later"))
    assert "req |-> ##3 ack" in plan.assertion


def test_planner_supports_bounded_consecutive_repetition_response():
    plan = plan_requirement(Requirement("REQ-REQ-RESP-3", "req stays high for 3 consecutive cycles and resp is high afterwards"))
    assert "req[*3] |-> resp" in plan.assertion


def test_planner_supports_bounded_response_window():
    plan = plan_requirement(Requirement("REQ-REQ-ACK-WINDOW", "req is high and ack becomes high within 3 cycles"))
    assert "req |-> ##[1:3] ack" in plan.assertion


def test_planner_supports_bounded_hold_until_response():
    plan = plan_requirement(Requirement("REQ-REQ-ACK-UNTIL", "req remains high until ack is high within 3 cycles"))
    assert "req[*0:2] ##[1:3] ack" in plan.assertion


def test_planner_supports_compound_boolean_requirements():
    plans = plan_ir(VerificationIR(requirements=[
        Requirement("REQ-VALID-READY-ACCEPT", "valid and ready implies accepted"),
        Requirement("REQ-VALID-OR-READY-ACCEPT", "valid or ready requires accepted"),
    ]))
    assert "(valid && ready) |-> accepted" in plans[0].assertion
    assert "(valid || ready) |-> accepted" in plans[1].assertion


def test_planner_supports_literal_decode_and_grant_mappings():
    decode = plan_requirement(Requirement("REQ-DEC", "opcode `2'd2` produces `4'b0100`"))
    grant = plan_requirement(Requirement("REQ-ARB", "request `2'b10`, grant is `2'b10`"))
    assert "opcode == 2'd2 |-> decode == 4'b0100" in decode.assertion
    assert "req == 2'b10 |-> grant == 2'b10" in grant.assertion


def test_planner_supports_onehot_and_onehot_or_zero_requirements():
    plans = plan_ir(VerificationIR(requirements=[
        Requirement("REQ-GRANT-ONEHOT", "grant is one-hot"),
        Requirement("REQ-GRANT-ONEHOT0", "grant is one-hot-or-zero"),
        Requirement("REQ-REQ-AT-MOST-ONE", "req has at most one active bit"),
    ]))
    assert "$onehot(grant)" in plans[0].assertion
    assert "$onehot0(grant)" in plans[1].assertion
    assert "$onehot0(req)" in plans[2].assertion


def test_planner_supports_mutual_exclusion_requirements():
    plan = plan_requirement(Requirement("REQ-ARBITRATION-MUTEX", "grant_a and grant_b are never high"))
    assert "!(grant_a && grant_b)" in plan.assertion
