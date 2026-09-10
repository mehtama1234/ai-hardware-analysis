from deployment.collateral_store import CollateralStore
from deployment.project_execution import lint_project_rtl


def test_lint_project_rtl_records_verilator_front_end_result(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    record = store.add("p1", "counter.sv", "rtl", "r7", "module counter(input logic clk); endmodule\n")
    result = lint_project_rtl(record, collateral_root=tmp_path / "collateral", run_root=tmp_path / "run")
    assert result["status"] == "passed"
    assert result["tool_run"]["tool"] == "verilator-project-lint"
