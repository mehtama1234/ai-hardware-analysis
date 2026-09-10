from deployment.collateral_store import CollateralStore
from deployment.project_execution import simulate_project_regression


def test_project_regression_retains_each_testbench_case(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    rtl = store.add("p1", "counter.sv", "rtl", "r1", "module counter(input logic clk); endmodule\n")
    tb_text = 'module tb; initial begin $dumpfile("waveform.vcd"); $dumpvars; $finish; end endmodule\n'
    tb1 = store.add("p1", "tb1.sv", "testbench", "r1", tb_text)
    tb2 = store.add("p1", "tb2.sv", "testbench", "r1", tb_text)
    result = simulate_project_regression(rtl, [tb1, tb2], collateral_root=tmp_path / "collateral", run_root=tmp_path / "run", source_revision="r1")
    assert result["status"] == "passed"
    assert result["case_count"] == 2
    assert (tmp_path / "run/case-001/artifact-manifest.json").is_file()
    assert (tmp_path / "run/case-002/artifact-manifest.json").is_file()
