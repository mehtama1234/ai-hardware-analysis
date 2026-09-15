from pathlib import Path
from verification_platform.simulation import probe_verilator_capability_matrix, probe_verilator_options, run_iverilog_vvp, run_verilator_lint

def test_simulation_adapter_records_expected_artifacts(tmp_path):
    dut = tmp_path / "dut.sv"; tb = tmp_path / "tb.sv"
    dut.write_text("module dut(input logic clk, output logic q); always_ff @(posedge clk) q <= 1'b1; endmodule\n")
    tb.write_text("module tb; logic clk=0; logic q; dut d(clk,q); always #1 clk=~clk; initial begin $dumpfile(\"waveform.vcd\"); $dumpvars; #3 $finish; end endmodule\n")
    compile_run, sim_run = run_iverilog_vvp(dut, tb, run_root=tmp_path / "run", source_revision="test-v1", binary_name="dut.vvp", tool_prefix="test")
    assert compile_run.status == "passed" and sim_run is not None and sim_run.status == "passed"
    assert (tmp_path / "run" / "waveform.vcd").is_file()

def test_verilator_lint_adapter_records_a_static_check(tmp_path):
    dut = tmp_path / "dut.sv"
    dut.write_text("module dut(input logic a, output logic y); assign y=a; endmodule\n")
    run = run_verilator_lint(dut, run_root=tmp_path / "lint", source_revision="test-v1", top="dut")
    assert run.status == "passed"


def test_verilator_lint_resolves_sources_when_runner_changes_working_directory(tmp_path):
    dut = tmp_path / "dut.sv"
    dut.write_text("module dut(input logic a, output logic y); assign y=a; endmodule\n")
    run = run_verilator_lint(str(dut), run_root=tmp_path / "lint", source_revision="test-v1", top="dut")
    assert run.status == "passed"
    assert str(dut.resolve()) in run.command


def test_verilator_option_probe_records_unsupported_timing_flag_without_passing(tmp_path):
    result = probe_verilator_options(["--timing"], run_root=tmp_path / "probe", source_revision="test-v1")
    assert result["status"] == "unsupported"
    assert result["tool_run"]["status"] == "failed"
    assert (tmp_path / "probe" / "verilator-option-probe.json").is_file()


def test_verilator_capability_matrix_checks_flags_against_real_rtl(tmp_path):
    dut = tmp_path / "dut.sv"
    dut.write_text("module dut(input logic clk, output logic q); always_ff @(posedge clk) q <= 1'b0; endmodule\n")
    result = probe_verilator_capability_matrix(
        [dut], top="dut", options=["--timing", "--assert"],
        run_root=tmp_path / "matrix", source_revision="matrix-v1",
    )
    assert result["status"] == "blocked"
    assert "--timing" in result["unsupported_options"]
    assert result["probes"][0]["tool_run"]["status"] == "failed"
    assert (tmp_path / "matrix/verilator-capability-matrix.json").is_file()
