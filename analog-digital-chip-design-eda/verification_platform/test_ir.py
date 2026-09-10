from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.ir import EvidenceRef, Requirement, VerificationIR


def test_ir_is_deterministic_and_links_evidence(tmp_path):
    evidence = EvidenceRef("runs/1/failure.log", "a" * 64, "tool-log", "abc123")
    ir = VerificationIR(
        design_revision="abc123",
        requirements=[Requirement("REQ-RESET", "Reset drives outputs to zero", "passed", [evidence])],
        tool_runs=[{"id": "run-1", "tool": "iverilog", "status": "passed", "artifacts": [evidence.path]}],
    )
    first = ir.digest()
    output = tmp_path / "ir.json"
    assert ir.write(output) == first
    assert output.read_text(encoding="utf-8").endswith("\n")
    assert VerificationIR(design_revision="different").digest() != first


def test_duplicate_requirement_ids_are_rejected():
    ir = VerificationIR(requirements=[Requirement("REQ-1", "a"), Requirement("REQ-1", "b")])
    try:
        ir.validate()
    except ValueError as exc:
        assert "duplicate requirement" in str(exc)
    else:
        raise AssertionError("duplicate IDs must be rejected")


def test_ir_rejects_dangling_check_requirement():
    ir = VerificationIR(requirements=[Requirement("REQ-1", "reset")], checks=[{"id": "CHECK-2", "requirement_id": "REQ-2"}])
    try:
        ir.validate()
    except ValueError as exc:
        assert "unknown requirement" in str(exc)
    else:
        raise AssertionError("dangling check links must be rejected")
