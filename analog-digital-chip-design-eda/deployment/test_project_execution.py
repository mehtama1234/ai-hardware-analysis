import json

from deployment.collateral_store import CollateralStore
from deployment.project_execution import compile_project_rtl


def test_compile_project_rtl_records_open_source_tool_evidence(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    record = store.add("p1", "counter.sv", "rtl", "r7", "module counter(input logic clk); endmodule\n")
    result = compile_project_rtl(record, collateral_root=tmp_path / "collateral", run_root=tmp_path / "run")
    assert result["status"] == "passed"
    assert result["top_module"] == "counter"
    assert result["tool_run"]["tool"] == "iverilog-project-compile"
    assert json.loads((tmp_path / "run/project-compile-result.json").read_text())["exit_code"] == 0


def test_compile_project_rtl_rejects_tampered_content(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    record = store.add("p1", "counter.sv", "rtl", "r7", "module counter(input logic clk); endmodule\n")
    source = tmp_path / "collateral" / str(record["path"])
    source.write_text("module counter(input logic clk); assign broken = ; endmodule\n")
    try:
        compile_project_rtl(record, collateral_root=tmp_path / "collateral", run_root=tmp_path / "run")
    except ValueError as error:
        assert "content hash" in str(error)
    else:
        raise AssertionError("tampered collateral must be rejected")
