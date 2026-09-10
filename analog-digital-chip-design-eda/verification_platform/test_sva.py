from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.sva import compile_sva_with_iverilog, compile_sva_with_verilator


def test_iverilog_capability_failure_is_recorded(tmp_path):
    source = tmp_path / "checks.sv"
    source.write_text("module checks(input logic clk, input logic q); assert property (@(posedge clk) q |=> q); endmodule\n", encoding="utf-8")
    run = compile_sva_with_iverilog(source, run_root=tmp_path / "run", source_revision="r1")
    assert run.tool == "iverilog-sva"
    assert run.status == "failed"  # Icarus in this environment lacks concurrent assertion support.


def test_verilator_capability_failure_is_recorded(tmp_path):
    source = tmp_path / "checks.sv"
    source.write_text("module checks(input logic clk, input logic q); assert property (@(posedge clk) q |=> q); endmodule\n", encoding="utf-8")
    run = compile_sva_with_verilator(source, run_root=tmp_path / "run", source_revision="r1")
    assert run.tool == "verilator-sva"
    assert run.status == "failed"
