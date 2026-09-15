from pathlib import Path
import sys

from verification_platform.svm import run_synthesizable_checker
from verification_platform.orchestration import run_four_workstream_pipeline


def _fixture(tmp_path: Path, *, broken: bool = False):
    dut = tmp_path / "dut.sv"
    dut.write_text(
        "module counter(input logic clk, input logic rst, input logic enable, output logic [3:0] q); "
        "always_ff @(posedge clk) if (rst) q <= 4'd0; else if (enable) q <= q + 4'd1; endmodule\n"
        if not broken else
        "module counter(input logic clk, input logic rst, input logic enable, output logic [3:0] q); "
        "always_ff @(posedge clk) if (rst) q <= 4'd0; else if (enable) q <= q + 4'd2; endmodule\n",
        encoding="utf-8",
    )
    checker = tmp_path / "checker.sv"
    checker.write_text(
        "module counter_svm(input logic clk, input logic rst, input logic enable, input logic [3:0] actual, output logic mismatch); "
        "logic [3:0] reference; always_ff @(posedge clk) begin "
        "if (rst) begin reference <= 4'd0; mismatch <= 1'b0; end else begin "
        "if (enable) reference <= reference + 4'd1; "
        "if (actual !== reference) begin mismatch <= 1'b1; end end "
        "end endmodule\n",
        encoding="utf-8",
    )
    harness = tmp_path / "harness.sv"
    harness.write_text(
        "module svm_harness; logic clk=0; logic rst=1; logic enable=0; logic [3:0] q; logic mismatch; "
        "counter dut(.clk(clk), .rst(rst), .enable(enable), .q(q)); "
        "counter_svm check(.clk(clk), .rst(rst), .enable(enable), .actual(q), .mismatch(mismatch)); "
        "always #5 clk = ~clk; always @(posedge clk) if (mismatch) $display(\"SVM_MISMATCH cycle=1 actual=%0d expected=%0d\", q, 0); "
        "initial begin #12 rst=0; enable=1; #30 enable=0; #2; $display(\"SVM_CYCLES cycles=4\"); "
        "if (!mismatch) $display(\"SVM_PASS\"); $finish; end endmodule\n",
        encoding="utf-8",
    )
    return dut, checker, harness


def test_synthesizable_checker_passes_clean_dut(tmp_path: Path):
    dut, checker, harness = _fixture(tmp_path)
    result = run_synthesizable_checker([dut], checker, harness, top="svm_harness", run_root=tmp_path / "run", source_revision="svm-v1")
    assert result["status"] == "passed"
    assert result["pass_marker_present"] is True
    assert result["mismatch_marker_present"] is False
    assert result["performance"]["status"] == "measured"
    assert result["performance"]["cycles"] == 4
    assert (tmp_path / "run/svm-result.json").is_file()


def test_synthesizable_checker_blocks_injected_mismatch(tmp_path: Path):
    dut, checker, harness = _fixture(tmp_path, broken=True)
    result = run_synthesizable_checker([dut], checker, harness, top="svm_harness", run_root=tmp_path / "run", source_revision="svm-broken-v1")
    assert result["status"] == "blocked"
    assert result["mismatch_marker_present"] is True
    assert result["pass_marker_present"] is False
    assert result["mismatch_count"] >= 1
    assert result["mismatch_records"][0]["cycle"] == 1
    assert "actual" in result["mismatch_records"][0]


def test_four_workstream_pipeline_can_checkpoint_svm_stage(tmp_path: Path):
    dut, checker, harness = _fixture(tmp_path)
    spec = tmp_path / "spec.md"
    spec.write_text("REQ-RESET: q is zero while rst is asserted\n", encoding="utf-8")
    protocol = tmp_path / "protocol.json"
    protocol.write_text(
        '{"schema_version":"protocol-plan-v1","name":"svm","addr_width":8,"data_width":32,"steps":[{"operation":"read","address":0,"expected":0}]}\n',
        encoding="utf-8",
    )
    result = run_four_workstream_pipeline(
        spec, [dut], top="counter", protocol_plan=protocol,
        command=[sys.executable, "-c", "print('ok')"], tool="python",
        run_root=tmp_path / "pipeline", source_revision="svm-pipeline-v1",
        svm_checker_source=checker, svm_harness=harness,
    )
    assert result["status"] == "passed"
    assert result["svm"]["status"] == "passed"
    checkpoint = (tmp_path / "pipeline/workflow-checkpoint.json").read_text(encoding="utf-8")
    assert "svm/svm-result.json" in checkpoint
