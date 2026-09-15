from pathlib import Path

from verification_platform.debug import analyze_failure, build_replay_slice, generate_filtered_dut, generate_hierarchical_filtered_dut, prove_filtered_dut_equivalence, prove_hierarchical_filtered_dut_equivalence, write_debug_package


def _inputs(tmp_path: Path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("module dut(input clk, input enable, output reg out); always @(posedge clk) out <= enable; endmodule\n", encoding="utf-8")
    wave = tmp_path / "trace.vcd"
    wave.write_text("$var wire 1 ! enable $end\n$var wire 1 \\\" out $end\n$enddefinitions $end\n#0\n0!\n0\\\"\n#5\n1!\n1\\\"\n", encoding="utf-8")
    return rtl, wave


def test_debug_package_composes_frontier_graph_and_balanced_diagnosis(tmp_path: Path):
    rtl, wave = _inputs(tmp_path)
    package = analyze_failure(wave, rtl, signal="out", observed=[(0, "0"), (5, "1")], reference=[(0, "0"), (5, "0")], source_revision="v1", for_evidence=["out diverges at cycle 1"], against_evidence=["the assignment is syntactically valid"])
    assert package["status"] == "review_required"
    assert package["state_frontier"]["cycle"] == 1
    assert package["replay_slice"]["status"] == "ready"
    assert package["diagnosis"]["status"] == "review_required"
    assert package["root_cause_candidates"]["status"] == "available"
    assert package["root_cause_candidates"]["candidates"][0]["line"] == 1
    assert package["competing_hypotheses"]["status"] == "available"
    assert package["competing_hypotheses"]["hypotheses"][0]["status"] == "review_required"
    assert package["causal_timeline"]["status"] == "available"
    assert package["causal_timeline"]["frontier_node"] == package["causal_frontier_binding"]["frontier_node"]
    assert package["causal_timeline_validation"]["status"] == "passed"
    assert write_debug_package(package, tmp_path / "debug.json").is_file()


def test_debug_package_blocks_ambiguous_alignment(tmp_path: Path):
    rtl, wave = _inputs(tmp_path)
    package = analyze_failure(wave, rtl, signal="out", observed=[(0, "0"), (5, "1")], reference=[(0, "0"), (5, "0")], source_revision="v1", for_evidence=["mismatch"], against_evidence=["possible expected behavior"], reference_traces={"count": [(0, "0")]}, rtl_traces={"lane_a": [(0, "0")], "lane_b": [(0, "0")]})
    assert package["status"] == "blocked"
    assert "ambiguous" in package["blocked_reason"]
    assert package["aligned_state_frontier"]["status"] == "blocked"


def test_replay_slice_is_bounded_and_digest_bound(tmp_path: Path):
    rtl, wave = _inputs(tmp_path)
    slice_record = build_replay_slice(rtl, signal="out", source_revision="v1")
    assert slice_record["status"] == "ready"
    assert slice_record["rtl_sha256"]
    assert slice_record["slice_sha256"]
    assert slice_record["dependency_paths"]
    package = analyze_failure(wave, rtl, signal="out", observed=[(0, "0"), (5, "1")], reference=[(0, "0"), (5, "0")], source_revision="v1", for_evidence=["mismatch"], against_evidence=["valid"])
    assert package["dependency_cdfg"]["schema_version"] == "dependency-cdfg-v1"
    assert any(item["line"] == 1 for item in slice_record["selected_lines"])


def test_filtered_dut_reconstructs_supported_dependency_cone(tmp_path: Path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("module dut(input logic a, input logic unused, output logic y);\nlogic b;\nassign b = a;\nassign y = b;\nassign unused = a;\nendmodule\n", encoding="utf-8")
    result = generate_filtered_dut(rtl, signal="y", source_revision="v1", output=tmp_path / "filtered.sv")
    assert result["status"] == "ready"
    text = (tmp_path / "filtered.sv").read_text(encoding="utf-8")
    assert "assign b = a;" in text and "assign y = b;" in text
    assert "assign unused = a;" not in text
    proof = prove_filtered_dut_equivalence(rtl, tmp_path / "filtered.sv", top="dut", run_root=tmp_path / "proof", source_revision="v1")
    assert proof["status"] == "proven"


def test_filtered_dut_rejects_hierarchical_reconstruction(tmp_path: Path):
    rtl = tmp_path / "hier.sv"
    rtl.write_text("module child(input a, output y); assign y = a; endmodule\nmodule top(input a, output y); child u(.a(a), .y(y)); endmodule\n", encoding="utf-8")
    result = generate_filtered_dut(rtl, signal="y", source_revision="v1", output=tmp_path / "filtered.sv")
    assert result["status"] == "blocked"
    assert "exactly one module" in result["blocked_reason"]


def test_hierarchical_filtered_dut_preserves_required_instances_and_drops_unrelated(tmp_path: Path):
    rtl = tmp_path / "hier.sv"
    rtl.write_text("module child(input logic a, input logic clk, output logic y); assign y = a; endmodule\nmodule unused(input a, output y); assign y = a; endmodule\nmodule top(input logic a, input logic clk, output logic y); child u_child(.a(a), .clk(clk), .y(y)); endmodule\n", encoding="utf-8")
    result = generate_hierarchical_filtered_dut(rtl, signal="y", source_revision="v1", output=tmp_path / "filtered.sv", top="top")
    assert result["status"] == "ready"
    assert result["selected_modules"] == ["child", "top"]
    text = (tmp_path / "filtered.sv").read_text(encoding="utf-8")
    assert "module child" in text and "module top" in text and "module unused" not in text
    proof = prove_hierarchical_filtered_dut_equivalence(rtl, tmp_path / "filtered.sv", top="top", selected_modules=result["selected_modules"], run_root=tmp_path / "proof", source_revision="v1")
    assert proof["status"] == "proven"


def test_hierarchical_filtered_dut_can_slice_explicit_leaf_target(tmp_path: Path):
    rtl = tmp_path / "hier.sv"
    rtl.write_text(
        "module child(input logic a, output logic y);\n"
        "  logic unused;\n"
        "  assign y = a;\n"
        "  assign unused = a;\n"
        "endmodule\n"
        "module top(input logic a, output logic y);\n"
        "  child u_child(.a(a), .y(y));\n"
        "endmodule\n",
        encoding="utf-8",
    )
    result = generate_hierarchical_filtered_dut(
        rtl, signal="y", source_revision="v1", output=tmp_path / "filtered.sv", top="top",
        module_targets={"child": "y"},
    )
    assert result["status"] == "ready"
    assert result["reduction"] == "hierarchy-preserving-dependency-cone"
    assert result["sliced_modules"] == ["child"]
    text = (tmp_path / "filtered.sv").read_text(encoding="utf-8")
    assert "assign y = a;" in text and "assign unused = a;" not in text
    proof = prove_hierarchical_filtered_dut_equivalence(rtl, tmp_path / "filtered.sv", top="top", selected_modules=result["selected_modules"], run_root=tmp_path / "proof", source_revision="v1")
    assert proof["status"] == "proven"
