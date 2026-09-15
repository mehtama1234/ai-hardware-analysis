from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.repair import RepairProposal, apply_to_copy, build_repair_patch_candidate, propose_enable_guard, run_approved_repair_retest
from verification_platform.triage import Failure


def test_repair_is_review_required_until_approved():
    proposal = propose_enable_guard(Failure(1, "counter_q", "0", "1"), requirement_id="REQ-COUNTER-HOLD", file="counter.sv", line=7)
    assert proposal.decision() == "review_required"
    assert proposal.decision(human_approved=True) == "allowed"


def test_approved_repair_writes_only_a_copy(tmp_path):
    source = tmp_path / "counter.sv"
    source.write_text("counter_q <= counter_q + 4'd1;\n", encoding="utf-8")
    proposal = propose_enable_guard(Failure(1, "counter_q", "0", "1"), requirement_id="REQ-COUNTER-HOLD", file="counter.sv", line=1)
    destination = apply_to_copy(source, tmp_path / "patched.sv", proposal, human_approved=True)
    assert "if (enable)" in destination.read_text(encoding="utf-8")
    assert "if (enable)" not in source.read_text(encoding="utf-8")


def test_approved_repair_retest_preserves_scope_and_source(tmp_path: Path):
    source = tmp_path / "counter.sv"
    source.write_text("module counter(output logic q); always_comb q = 1'b0; endmodule\n", encoding="utf-8")
    tb = tmp_path / "tb.sv"
    tb.write_text("module tb; logic q; counter dut(q); endmodule\n", encoding="utf-8")
    proposal = RepairProposal("REQ-1", "counter.sv", 1, "1'b0", "1'b0", "bounded no-op test repair")
    run_root = tmp_path / "run"
    command = ["iverilog", "-g2012", "-o", str(run_root / "dut.vvp"), str(source), str(tb)]
    original = source.read_bytes()
    result = run_approved_repair_retest(source, tmp_path / "repaired.sv", proposal, command, run_root=run_root, source_revision="v1", expected_artifacts=["dut.vvp"], human_approved=True)
    assert result["status"] == "passed"
    assert result["original_source_unchanged"] is True
    assert result["tool_run"]["command"][4] == str(tmp_path / "repaired.sv")
    assert source.read_bytes() == original


def test_repair_retest_fails_closed_when_command_fails(tmp_path: Path):
    source = tmp_path / "counter.sv"
    source.write_text("q <= q + 4'd1;\n", encoding="utf-8")
    proposal = RepairProposal("REQ-1", "counter.sv", 1, "q <= q + 4'd1;", "if (enable) q <= q + 4'd1;", "guard increment")
    result = run_approved_repair_retest(
        source, tmp_path / "repaired.sv", proposal,
        [sys.executable, "-c", "raise SystemExit(3)", str(source)],
        run_root=tmp_path / "failed-run", source_revision="v1", human_approved=True,
    )
    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "repair retest command did not pass"
    assert result["original_source_unchanged"] is True


def test_repair_patch_candidate_is_hash_and_exact_text_bound(tmp_path: Path):
    source = tmp_path / "dut.sv"
    source.write_text("always @(posedge clk) q <= q + 1'b1;\n", encoding="utf-8")
    result = build_repair_patch_candidate(
        {"proposal_id": "p1", "before": "q <= q + 1'b1;", "after": "if (enable) q <= q + 1'b1;"},
        source, source_revision="v1", evidence=["debug-package.json"],
    )
    assert result["status"] == "review_required"
    assert result["line"] == 1
    assert result["source_sha256"]
    assert result["candidate_sha256"]


def test_repair_patch_candidate_rejects_stale_or_ambiguous_edit(tmp_path: Path):
    source = tmp_path / "dut.sv"
    source.write_text("q <= 1;\nq <= 1;\n", encoding="utf-8")
    with pytest.raises(ValueError, match="exactly one"):
        build_repair_patch_candidate({"before": "q <= 1;", "after": "q <= 0;"}, source, source_revision="v1", evidence=["evidence"])
    with pytest.raises(ValueError, match="digest"):
        build_repair_patch_candidate({"before": "q <= 1;\nq <= 1;", "after": "q <= 0;", "source_sha256": "0" * 64}, source, source_revision="v1", evidence=["evidence"])


def test_repair_patch_candidate_rejects_unknown_edit_operator(tmp_path: Path):
    source = tmp_path / "dut.sv"
    source.write_text("q <= 1;\n", encoding="utf-8")
    with pytest.raises(ValueError, match="edit_operator"):
        build_repair_patch_candidate(
            {"before": "q <= 1;", "after": "q <= 0;", "edit_operator": "rewrite_ast"},
            source, source_revision="v1", evidence=["evidence"],
        )


def test_repair_patch_candidate_requires_ranked_causal_location_when_supplied(tmp_path: Path):
    source = tmp_path / "dut.sv"
    source.write_text("assign safe = a;\nassign target = b;\n", encoding="utf-8")
    with pytest.raises(ValueError, match="root-cause location"):
        build_repair_patch_candidate(
            {"before": "assign safe = a;", "after": "assign safe = b;"}, source,
            source_revision="v1", evidence=["debug.json"],
            allowed_source_locations=[{"file": str(source), "line": 2}],
        )
    result = build_repair_patch_candidate(
        {"before": "assign target = b;", "after": "assign target = a;"}, source,
        source_revision="v1", evidence=["debug.json"],
        allowed_source_locations=[{"file": str(source), "line": 2}],
    )
    assert result["root_cause_location_bound"] is True
