from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.formal import counterexample_to_failure, parse_yosys_counterexample, parse_yosys_sat_result, yosys_sat_prove, yosys_syntax_check


def test_yosys_preflight_records_formal_stage(tmp_path):
    rtl = tmp_path / "counter.sv"
    rtl.write_text("module counter(input logic clk, output logic q); always_ff @(posedge clk) q <= 1'b0; endmodule\n", encoding="utf-8")
    run = yosys_syntax_check(rtl, run_root=tmp_path / "run", top="counter", source_revision="r1")
    assert run.tool == "yosys-formal-preflight"
    assert run.status == "passed"


def test_yosys_sat_proves_constant_invariant(tmp_path):
    rtl = tmp_path / "constant.sv"
    rtl.write_text("module constant(input clk, output reg q); always @(posedge clk) q <= 1'b0; endmodule\n", encoding="utf-8")
    run = yosys_sat_prove(rtl, top="constant", signal="q", expected_value="0", run_root=tmp_path / "sat", source_revision="r1")
    assert run.tool == "yosys-sat"
    assert run.status == "passed"


def test_yosys_result_parser_distinguishes_proof_and_counterexample():
    assert parse_yosys_sat_result("SAT proof finished - no model found") == "proven"
    assert parse_yosys_sat_result("SAT proof finished - model found: FAIL!") == "counterexample"
    assert parse_yosys_sat_result("solver unavailable") == "unknown"


def test_yosys_counterexample_parser_extracts_time_signal_values():
    log = """SAT proof finished - model found: FAIL!\n   Time Signal Name             Dec       Hex           Bin\n   init \\q                        0         0         0\n      1 \\q                        0         0         0\n      2 \\q                        1         1         1\n"""
    assert parse_yosys_counterexample(log) == [
        {"time": "init", "signal": "q", "decimal": 0, "binary": "0"},
        {"time": 1, "signal": "q", "decimal": 0, "binary": "0"},
        {"time": 2, "signal": "q", "decimal": 1, "binary": "1"},
    ]
    assert parse_yosys_counterexample("SAT proof finished - no model found") == []


def test_yosys_sat_run_persists_counterexample_artifact(tmp_path):
    rtl = tmp_path / "bad.sv"
    rtl.write_text("module bad(input clk, output reg q); always @(posedge clk) q <= 1'b1; endmodule\n", encoding="utf-8")
    run_root = tmp_path / "counterexample"
    run = yosys_sat_prove(rtl, top="bad", signal="q", expected_value="0", run_root=run_root, sequence=2, source_revision="bad-v1")
    assert run.status == "passed"  # the adapter ran; the proof result is classified separately
    assert run.metadata["proof_result"] == "counterexample"
    log = (run_root / "stdout.log").read_text(encoding="utf-8")
    assert parse_yosys_sat_result(log) == "counterexample"
    rows = parse_yosys_counterexample(log)
    assert rows[-1]["signal"] == "q"
    assert rows[-1]["decimal"] == 1
    failure = counterexample_to_failure(log, signal="q", expected_value="0")
    assert failure is not None
    assert failure.cycle == 2 and failure.actual == "1"
