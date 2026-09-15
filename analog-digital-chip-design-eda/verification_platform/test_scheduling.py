import json
from pathlib import Path

from verification_platform.scheduling import lint_time_zero, run_scheduling_gate, run_time_zero_regression, write_time_zero_lint


def test_time_zero_lint_blocks_dynamic_initial_construction(tmp_path: Path):
    source = tmp_path / "unsafe.sv"
    source.write_text("initial begin agent = new(); end\n", encoding="utf-8")
    report = lint_time_zero([source], root=tmp_path)
    assert report["status"] == "blocked"
    assert report["findings"][0]["rule_id"] == "TIMEZERO-DYNAMIC-NEW"
    assert write_time_zero_lint(tmp_path / "lint.json", report).is_file()


def test_time_zero_lint_flags_constructor_zero_delay(tmp_path: Path):
    source = tmp_path / "unsafe.sv"
    source.write_text("function new(string name); #0; endfunction\n", encoding="utf-8")
    report = lint_time_zero([source], root=tmp_path)
    assert report["status"] == "blocked"
    assert any(item["rule_id"] == "TIMEZERO-CONSTRUCTOR-DELAY" for item in report["findings"])


def test_time_zero_lint_requires_review_for_objections_but_allows_clean_code(tmp_path: Path):
    source = tmp_path / "uvm.sv"
    source.write_text("task run_phase(); phase.raise_objection(this); phase.drop_objection(this); endtask\n", encoding="utf-8")
    report = lint_time_zero([source], root=tmp_path)
    assert report["status"] == "passed"
    assert len(report["findings"]) == 2
    body = {key: value for key, value in report.items() if key != "report_sha256"}
    import hashlib
    assert report["report_sha256"] == hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def test_scheduling_gate_compiles_only_after_lint_passes(tmp_path: Path):
    source = tmp_path / "clean.sv"
    source.write_text("module clean(input logic clk, output logic q); always_ff @(posedge clk) q <= 1'b0; endmodule\n", encoding="utf-8")
    result = run_scheduling_gate([source], run_root=tmp_path / "run", source_revision="v1")
    assert result["status"] == "passed"
    assert result["compiler"]["status"] == "passed"


def test_scheduling_gate_blocks_before_compiler_on_time_zero_error(tmp_path: Path):
    source = tmp_path / "unsafe.sv"
    source.write_text("initial begin agent = new(); end\n", encoding="utf-8")
    result = run_scheduling_gate([source], run_root=tmp_path / "run", source_revision="v1")
    assert result["status"] == "blocked"
    assert result["compiler"] is None


def test_time_zero_regression_compiles_and_runs_with_explicit_pass_marker(tmp_path: Path):
    source = tmp_path / "timezero.sv"
    source.write_text("module timezero; initial begin #0; $display(\"TIMEZERO_REGRESSION_PASS\"); $finish; end endmodule\n", encoding="utf-8")
    result = run_time_zero_regression(source, run_root=tmp_path / "run", source_revision="v1")
    assert result["status"] == "passed"
    assert result["outcome"] == "normal_completion"
    assert result["compile"]["status"] == "passed"
    assert result["simulation"]["status"] == "passed"


def test_time_zero_regression_classifies_premature_termination(tmp_path: Path):
    source = tmp_path / "premature.sv"
    source.write_text("module premature; initial begin $display(\"TIMEZERO_PREMATURE_TERMINATION\"); $finish; end endmodule\n", encoding="utf-8")
    result = run_time_zero_regression(source, run_root=tmp_path / "run", source_revision="v1")
    assert result["status"] == "blocked"
    assert result["outcome"] == "premature_time_zero_termination"


def test_time_zero_regression_classifies_missing_stimulus(tmp_path: Path):
    source = tmp_path / "silent.sv"
    source.write_text("module silent; initial begin #1; $finish; end endmodule\n", encoding="utf-8")
    result = run_time_zero_regression(source, run_root=tmp_path / "run", source_revision="v1")
    assert result["status"] == "blocked"
    assert result["outcome"] == "missing_stimulus"
