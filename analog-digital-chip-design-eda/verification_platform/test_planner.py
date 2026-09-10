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
