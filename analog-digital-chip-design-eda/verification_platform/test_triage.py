from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.triage import Failure, failure_to_ir, locate_source_marker, parse_failure


def test_parse_failure_is_structured():
    assert parse_failure("noise\nFAIL cycle=4 signal=data_q expected=0 actual=3\n") == Failure(4, "data_q", "0", "3")
    assert parse_failure("PASS\n") is None


def test_failure_projects_to_ir_with_hashed_evidence(tmp_path):
    (tmp_path / "simulation.log").write_text("FAIL cycle=1 signal=counter_q expected=0 actual=1\n", encoding="utf-8")
    (tmp_path / "waveform.vcd").write_text("$end\n", encoding="utf-8")
    ir = failure_to_ir(Failure(1, "counter_q", "0", "1"), root=tmp_path, source_revision="rev-1", artifact_paths=["simulation.log", "waveform.vcd"])
    assert ir.requirements[0].status == "failed"
    assert len(ir.requirements[0].evidence) == 2
    assert ir.tool_runs[0]["failure"]["actual"] == "1"


def test_source_marker_must_be_unique(tmp_path):
    source = tmp_path / "dut.sv"
    source.write_text("a // BUG\nb // BUG\n", encoding="utf-8")
    try:
        locate_source_marker(source, "BUG")
    except ValueError as exc:
        assert "exactly one" in str(exc)
    else:
        raise AssertionError("ambiguous source markers must be rejected")
