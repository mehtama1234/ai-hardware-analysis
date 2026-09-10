from pathlib import Path
from verification_platform.simulation import run_iverilog_vvp, run_verilator_lint

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
