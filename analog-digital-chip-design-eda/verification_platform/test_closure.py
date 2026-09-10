from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.closure import evaluate_closure
from verification_platform.ir import EvidenceRef, Requirement, VerificationIR


def test_failed_requirement_cannot_be_closed():
    ir = VerificationIR(requirements=[Requirement("REQ-1", "output is zero", "failed")], tool_runs=[{"id": "run", "tool": "sim", "status": "passed"}])
    result = evaluate_closure(ir)[0]
    assert result.status == "failed"


def test_evidence_and_passed_run_are_required():
    ir = VerificationIR(requirements=[Requirement("REQ-1", "output is zero", "planned", [EvidenceRef("log", "a" * 64, "log")])])
    assert evaluate_closure(ir)[0].status == "open"
    ir.tool_runs = [{"id": "run", "tool": "sim", "status": "passed"}]
    assert evaluate_closure(ir)[0].status == "proven"


def test_failed_run_keeps_other_evidence_open():
    evidence = EvidenceRef("evidence.log", "a" * 64, "log")
    ir = VerificationIR(requirements=[Requirement("REQ-1", "x", "planned", [evidence])], tool_runs=[{"id": "pass", "tool": "sim", "status": "passed"}, {"id": "fail", "tool": "sim", "status": "failed"}])
    result = evaluate_closure(ir)[0]
    assert result.status == "open"
    assert "failed" in result.reason
