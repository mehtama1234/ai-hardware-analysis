from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.formal import counterexample_to_failure, generate_assertion_wrapper, parse_yosys_counterexample, parse_yosys_sat_result, run_yosys_antecedent_reachability, run_yosys_assertion_proof, run_yosys_signal_reachability, yosys_sat_prove, yosys_syntax_check


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


def test_yosys_assertion_proof_classifies_formal_model_counterexample(tmp_path: Path):
    root = Path(__file__).parents[1]
    result = run_yosys_assertion_proof(
        [root / "benchmarks/seeded_counter/counter.sv", root / "benchmarks/seeded_counter/formal_model_check.sv"],
        top="formal_model_check", run_root=tmp_path / "assertion-proof", sequence=6, source_revision="seeded-counter-v1",
    )
    assert result["status"] == "counterexample"
    assert result["solver_result"] == "counterexample"
    assert result["assertion_count"] == 1
    assert (tmp_path / "assertion-proof/assertion-proof-result.json").is_file()


def test_assertion_wrapper_validates_ports_and_compiles(tmp_path: Path):
    dut = tmp_path / "dut.sv"
    assertion = tmp_path / "assertion.sv"
    dut.write_text("module dut(input logic clk, input logic req, output logic grant); assign grant = req; endmodule\n", encoding="utf-8")
    assertion.write_text("module agent_assertion(input logic clk, input logic req, input logic grant); always @(posedge clk) assert (req == grant); endmodule\n", encoding="utf-8")
    result = generate_assertion_wrapper(dut, assertion, top="dut", output=tmp_path / "wrapper.sv", run_root=tmp_path / "wrapper", source_revision="v1")
    assert result["status"] == "passed"
    assert result["compiler"]["status"] == "passed"
    assert ".req(req)" in (tmp_path / "wrapper.sv").read_text(encoding="utf-8")


def test_assertion_wrapper_blocks_unknown_signal(tmp_path: Path):
    dut = tmp_path / "dut.sv"
    assertion = tmp_path / "assertion.sv"
    dut.write_text("module dut(input clk, output q); assign q = clk; endmodule\n", encoding="utf-8")
    assertion.write_text("module agent_assertion(input clk, input internal_state); endmodule\n", encoding="utf-8")
    result = generate_assertion_wrapper(dut, assertion, top="dut", output=tmp_path / "wrapper.sv", run_root=tmp_path / "wrapper", source_revision="v1")
    assert result["status"] == "blocked"
    assert "unknown DUT signals" in result["blocked_reason"]


def test_assertion_wrapper_can_explicitly_observe_declared_internal_signal(tmp_path: Path):
    dut = tmp_path / "dut.sv"
    assertion = tmp_path / "assertion.sv"
    dut.write_text("module dut(input logic clk, input logic req, output logic grant); logic internal_state; assign internal_state = req; assign grant = internal_state; endmodule\n", encoding="utf-8")
    assertion.write_text("module agent_assertion(input logic clk, input logic internal_state); endmodule\n", encoding="utf-8")
    result = generate_assertion_wrapper(dut, assertion, top="dut", output=tmp_path / "wrapper.sv", run_root=tmp_path / "wrapper", source_revision="v1", allow_internal_signals=True)
    assert result["status"] == "passed"
    assert result["internal_signals"] == ["internal_state"]
    assert ".internal_state(dut_i.internal_state)" in (tmp_path / "wrapper.sv").read_text(encoding="utf-8")


def test_yosys_signal_reachability_classifies_bounded_sat_and_unsat(tmp_path: Path):
    source = tmp_path / "reach.sv"
    source.write_text("module reach(input clk, output reg q); always @(posedge clk) q <= 1'b0; endmodule\n", encoding="utf-8")
    unreachable = run_yosys_signal_reachability(source, top="reach", signal="q", value="1", run_root=tmp_path / "unreachable", source_revision="v1")
    assert unreachable["status"] == "unreachable"
    reachable_source = tmp_path / "reachable.sv"
    reachable_source.write_text("module reachable(input clk, input en, output reg q); always @(posedge clk) if (en) q <= 1'b1; endmodule\n", encoding="utf-8")
    reachable = run_yosys_signal_reachability(reachable_source, top="reachable", signal="q", value="1", run_root=tmp_path / "reachable", source_revision="v1")
    assert reachable["status"] == "reachable"


def test_yosys_antecedent_reachability_handles_conjunction_and_disjunction(tmp_path: Path):
    source = tmp_path / "antecedent.sv"
    source.write_text("module antecedent(input clk, input req, input valid, output q); assign q = req & valid; endmodule\n", encoding="utf-8")
    result = run_yosys_antecedent_reachability(source, top="antecedent", antecedent="req && valid", allowed_signals={"req", "valid", "q"}, run_root=tmp_path / "conjunction", source_revision="v1")
    assert result["status"] == "reachable"
    disjunction = run_yosys_antecedent_reachability(source, top="antecedent", antecedent="req || valid", allowed_signals={"req", "valid"}, run_root=tmp_path / "or", source_revision="v1")
    assert disjunction["status"] == "reachable"
    blocked = run_yosys_antecedent_reachability(source, top="antecedent", antecedent="req || internal_state", allowed_signals={"req", "valid"}, run_root=tmp_path / "blocked", source_revision="v1")
    assert blocked["status"] == "blocked"
