from deployment.collateral_store import CollateralStore
from deployment.project_execution import formal_preflight_project_rtl


def test_formal_preflight_project_rtl_records_yosys_without_claiming_proof(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    record = store.add("p1", "counter.sv", "rtl", "r7", "module counter(input clk); wire q; assign q = clk; endmodule\n")
    result = formal_preflight_project_rtl(record, collateral_root=tmp_path / "collateral", run_root=tmp_path / "run")
    assert result["status"] == "passed"
    assert result["claim"] == "formal_preflight_only"
