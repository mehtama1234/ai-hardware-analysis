import json
from pathlib import Path
import subprocess

from verification_platform.lowering import generate_lowered_checker, lower_assertion, lower_plans, write_lowering_manifest
from verification_platform.ir import Requirement
from verification_platform.planner import plan_requirement


def test_lowering_records_clock_reset_and_temporal_transforms():
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) !enable |=> $stable(counter_q));",
        requirement_id="CHECK-REQ-COUNTER-HOLD",
    )
    assert prop.status == "supported"
    assert prop.clock == "clk"
    assert prop.reset == "rst"
    assert set(prop.transformations) == {"clock_alias_injection", "disable_iff_extraction", "sequence_delay_lowering"}
    assert "always @(posedge clk)" in prop.lowered
    assert "!(rst)" in prop.lowered


def test_lowering_supports_ranged_nonconsecutive_syntax():
    prop = lower_assertion(
        "assert property (@(posedge clk) a[=2:3] |-> c);",
        requirement_id="CHECK-UNSUPPORTED",
    )
    assert prop.status == "supported"
    assert prop.lowered is not None
    assert "ranged_nonconsecutive_repetition_lowering" in prop.transformations
    source = generate_lowered_checker([prop])
    assert "ranged non-consecutive repetition implication violated" in source


def test_lowering_manifest_is_self_digested(tmp_path: Path):
    plans = lower_plans([plan_requirement(Requirement("REQ-COUNTER-HOLD", "counter_q holds when enable is low"))])
    path = write_lowering_manifest(plans, tmp_path / "lowering.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    body = {key: value for key, value in payload.items() if key != "lowering_sha256"}
    import hashlib
    assert payload["lowering_sha256"] == hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def test_lowering_supports_simple_boolean_implications():
    same_cycle = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) request |-> grant);",
        requirement_id="CHECK-REQUEST-GRANT",
    )
    assert same_cycle.status == "supported"
    assert "boolean_implication_lowering" in same_cycle.transformations
    assert "request" in same_cycle.lowered and "!(grant)" in same_cycle.lowered
    next_cycle = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) request |=> grant);",
        requirement_id="CHECK-REQUEST-GRANT-NEXT",
    )
    assert next_cycle.status == "supported"
    assert "one_cycle_delay_lowering" in next_cycle.transformations
    assert "previous_CHECK_REQUEST_GRANT_NEXT" in next_cycle.lowered
    source = generate_lowered_checker([next_cycle])
    assert "input logic request" in source and "input logic grant" in source
    assert "logic previous_CHECK_REQUEST_GRANT_NEXT" in source


def test_lowering_supports_compound_boolean_implications():
    overlapped = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) valid && ready |-> accepted);",
        requirement_id="compound-overlap",
    )
    assert overlapped.status == "supported"
    assert "compound_boolean_implication_lowering" in overlapped.transformations
    assert "if ((valid && ready) && !(rst) && !(accepted))" in overlapped.lowered

    delayed = lower_assertion(
        "assert property (@(posedge clk) (valid || ready) |=> accepted);",
        requirement_id="compound-delayed",
    )
    assert delayed.status == "supported"
    assert "one_cycle_delay_lowering" in delayed.transformations
    assert "previous_compound_delayed <= (valid || ready);" in delayed.lowered


def test_lowering_supports_literal_mappings_and_numeric_invariants():
    mapping = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) opcode == 2'd2 |-> decode == 4'b0100);",
        requirement_id="CHECK-DEC",
    )
    assert mapping.status == "supported"
    assert "literal_mapping_lowering" in mapping.transformations
    invariant = lower_assertion("assert property (@(posedge clk) count <= 2);", requirement_id="CHECK-BOUND")
    assert invariant.status == "supported"
    assert "bounded_invariant_lowering" in invariant.transformations


def test_lowering_supports_mutual_exclusion_predicate():
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) !(grant_a && grant_b));",
        requirement_id="CHECK-ARBITRATION-MUTEX",
    )
    assert prop.status == "supported"
    assert "mutual_exclusion_predicate_lowering" in prop.transformations
    assert "(grant_a && grant_b) && !(rst)" in prop.lowered


def test_lowering_supports_gated_increment():
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) wr_en && count < 2 |=> count == $past(count) + 1'b1);",
        requirement_id="CHECK-FIFO-WRITE",
    )
    assert prop.status == "supported"
    assert "one_cycle_delay_lowering" in prop.transformations
    assert "previous_CHECK_FIFO_WRITE_value" in prop.lowered


def test_lowering_keeps_nested_compound_expression_blocked():
    lowered = lower_assertion(
        "assert property (@(posedge clk) ((valid && ready) || accept) |-> done);",
        requirement_id="nested-compound",
    )
    assert lowered.status == "unsupported"


def test_lowering_materializes_delayed_sequence_as_history_register():
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) request ##2 grant |-> response);",
        requirement_id="CHECK-REQUEST-GRANT-RESPONSE",
    )
    assert prop.status == "supported"
    assert "sequence_delay_lowering" in prop.transformations
    assert "logic [1:0] sequence_CHECK_REQUEST_GRANT_RESPONSE" in prop.lowered
    assert "delay_i < 2" in prop.lowered
    source = generate_lowered_checker([prop])
    assert "input logic request" in source and "input logic grant" in source and "input logic response" in source
    assert "logic [1:0] sequence_CHECK_REQUEST_GRANT_RESPONSE" in source


def test_lowering_materializes_fixed_cycle_response():
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) request |-> ##3 response);",
        requirement_id="CHECK-REQUEST-RESPONSE-3",
    )
    assert prop.status == "supported"
    assert "sequence_history_register" in prop.transformations
    assert "logic [2:0] sequence_CHECK_REQUEST_RESPONSE_3" in prop.lowered
    assert "delayed response violated" in prop.lowered


def test_lowering_materializes_planner_repetition_response():
    plan = plan_requirement(Requirement("REQ-REQ-RESP-3", "req stays high for 3 consecutive cycles and resp is high afterwards"))
    prop = lower_assertion(plan.assertion, requirement_id=plan.requirement_id)
    assert prop.status == "supported"
    assert "repetition_counter_lowering" in prop.transformations
    assert "repetition_REQ_REQ_RESP_3" in prop.lowered


def test_lowering_materializes_bounded_response_window():
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) req |-> ##[1:3] ack);",
        requirement_id="CHECK-REQ-ACK-WINDOW",
    )
    assert prop.status == "supported"
    assert "bounded_response_window_lowering" in prop.transformations
    assert "logic [2:0] response_active_CHECK_REQ_ACK_WINDOW" in prop.lowered
    assert "bounded response violated" in prop.lowered


def test_lowering_materializes_bounded_hold_until_response():
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) req |-> req[*0:2] ##[1:3] ack);",
        requirement_id="CHECK-REQ-ACK-UNTIL",
    )
    assert prop.status == "supported"
    assert "bounded_until_lowering" in prop.transformations
    assert "logic until_pending_CHECK_REQ_ACK_UNTIL" in prop.lowered
    assert "bounded until violated" in prop.lowered


def test_generated_bounded_hold_until_checker_compiles_with_iverilog(tmp_path: Path):
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) req |-> req[*0:2] ##[1:3] ack);",
        requirement_id="CHECK-REQ-ACK-UNTIL",
    )
    source = tmp_path / "lowered.sv"
    source.write_text(generate_lowered_checker([prop]), encoding="utf-8")
    result = subprocess.run(["iverilog", "-g2012", "-t", "null", str(source)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def _run_until_checker(tmp_path: Path, *, acknowledge: bool) -> subprocess.CompletedProcess[str]:
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) req |-> req[*0:2] ##[1:3] ack);",
        requirement_id="CHECK-REQ-ACK-UNTIL",
    )
    checker = tmp_path / "lowered.sv"
    checker.write_text(generate_lowered_checker([prop]), encoding="utf-8")
    harness = tmp_path / "tb.sv"
    ack_event = "ack = 1'b1;" if acknowledge else "ack = 1'b0;"
    harness.write_text(
        "module tb; logic clk=0, rst=1, enable=0, req=0, ack=0; logic [3:0] counter_q=0;\n"
        "always #5 clk = ~clk; lowered_checks dut(.clk(clk), .rst(rst), .enable(enable), .counter_q(counter_q), .req(req), .ack(ack));\n"
        "initial begin #12 rst=0; #3 req=1; #15 " + ack_event + " #35 $finish; end\nendmodule\n",
        encoding="utf-8",
    )
    binary = tmp_path / "sim.vvp"
    compile_result = subprocess.run(["iverilog", "-g2012", "-o", str(binary), str(checker), str(harness)], capture_output=True, text=True, check=False)
    assert compile_result.returncode == 0, compile_result.stderr
    return subprocess.run(["vvp", str(binary)], capture_output=True, text=True, check=False)


def test_bounded_hold_until_checker_accepts_in_window(tmp_path: Path):
    result = _run_until_checker(tmp_path, acknowledge=True)
    assert "ERROR" not in result.stdout + result.stderr


def test_bounded_hold_until_checker_reports_deadline_violation(tmp_path: Path):
    result = _run_until_checker(tmp_path, acknowledge=False)
    assert "bounded until violated" in result.stdout + result.stderr


def test_lowering_materializes_fixed_consecutive_repetition_as_counter():
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) request[*3] |-> response);",
        requirement_id="CHECK-REQUEST-REPEAT",
    )
    assert prop.status == "supported"
    assert "consecutive_repetition_lowering" in prop.transformations
    assert "integer repetition_CHECK_REQUEST_REPEAT" in prop.lowered
    assert "== 2" in prop.lowered
    source = generate_lowered_checker([prop])
    assert "input logic request" in source and "input logic response" in source


def test_lowering_supports_onehot_predicates_and_compiles(tmp_path: Path):
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) $onehot(grant));",
        requirement_id="CHECK-GRANT-ONEHOT",
    )
    assert prop.status == "supported"
    assert "onehot_predicate_lowering" in prop.transformations
    source_path = tmp_path / "onehot_lowered.sv"
    source_path.write_text(generate_lowered_checker([prop]), encoding="utf-8")
    result = subprocess.run(["iverilog", "-g2012", "-t", "null", "-s", "lowered_checks", str(source_path)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_lowering_supports_bounded_consecutive_repetition_range():
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) request[*2:4] |-> response);",
        requirement_id="CHECK-REQUEST-RANGE",
    )
    assert prop.status == "supported"
    assert "bounded_repetition_lowering" in prop.transformations
    assert "repetition_CHECK_REQUEST_RANGE >= 1" in prop.lowered
    assert "repetition_CHECK_REQUEST_RANGE == 3" in prop.lowered


def test_lowering_supports_fixed_nonconsecutive_repetition_counts():
    prop = lower_assertion(
        "assert property (@(posedge clk) disable iff (rst) request[=2] |-> response);",
        requirement_id="CHECK-REQUEST-NONCONSECUTIVE",
    )
    assert prop.status == "supported"
    assert "nonconsecutive_repetition_lowering" in prop.transformations
    assert "occurrences_CHECK_REQUEST_NONCONSECUTIVE == 1" in prop.lowered
    goto = lower_assertion(
        "assert property (@(posedge clk) request[->2] |-> response);",
        requirement_id="CHECK-REQUEST-GOTO",
    )
    assert goto.status == "supported"


def test_lowering_supports_ranged_nonconsecutive_repetition_counts():
    for operator, requirement in (("=", "CHECK-RANGE-EQUAL"), ("->", "CHECK-RANGE-GOTO")):
        prop = lower_assertion(
            f"assert property (@(posedge clk) disable iff (rst) request[{operator}2:4] |-> response);",
            requirement_id=requirement,
        )
        assert prop.status == "supported"
        assert "ranged_nonconsecutive_repetition_lowering" in prop.transformations
        sanitized = requirement.replace("-", "_")
        assert "occurrences_" + sanitized in prop.lowered
        assert "occurrences_" + sanitized + " >= 1" in prop.lowered


def test_lowering_rejects_reversed_nonconsecutive_range():
    prop = lower_assertion("assert property (@(posedge clk) request[=4:2] |-> response);", requirement_id="CHECK-REVERSED")
    assert prop.status == "unsupported"
    assert "minimum exceeds maximum" in (prop.reason or "")
