from deployment.collateral_store import CollateralStore
from deployment.project_execution import simulate_project


def test_simulate_project_projects_failure_and_waveform_into_triage(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    rtl = store.add("p1", "counter.sv", "rtl", "r7", "module counter(input logic clk, output logic q); always_ff @(posedge clk) q <= 1'b0; endmodule\n")
    tb = store.add("p1", "counter_tb.sv", "testbench", "r7", """module counter_tb;
  logic clk = 0; logic q; counter dut(.clk(clk), .q(q));
  always #5 clk = ~clk;
  initial begin $dumpfile(\"waveform.vcd\"); $dumpvars(0, counter_tb); #7;
    $display(\"FAIL cycle=1 signal=q expected=1 actual=%0d\", q);
    #8 $finish;
  end
endmodule
""")
    result = simulate_project(rtl, tb, collateral_root=tmp_path / "collateral", run_root=tmp_path / "run", source_revision="r7")
    assert result["status"] == "failed"
    assert result["failure"]["signal"] == "q"
    assert (tmp_path / "run/waveform.vcd").is_file()
    assert (tmp_path / "run/verification-ir.json").is_file()
    assert (tmp_path / "run/closure-report.json").read_text().find('"failed"') >= 0
    assert result["diagnosis"]["status"] == "review_required"


def test_simulate_project_persists_bounded_functional_coverage_marker(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    rtl = store.add("p1", "counter.sv", "rtl", "r7", "module counter(input logic clk); endmodule\n")
    tb = store.add("p1", "counter_tb.sv", "testbench", "r7", 'module counter_tb; initial begin $dumpfile("waveform.vcd"); $dumpvars(0, counter_tb); $display("COVERAGE kind=functional covered=3 total=4"); $finish; end endmodule\n')
    result = simulate_project(rtl, tb, collateral_root=tmp_path / "collateral", run_root=tmp_path / "run", source_revision="r7")
    assert result["status"] == "passed"
    assert result["coverage_path"].endswith("functional-coverage.json")
    from deployment.project_pov import build_project_pov
    assert build_project_pov(tmp_path / "run")["coverage"]["percentage"] == 75.0
