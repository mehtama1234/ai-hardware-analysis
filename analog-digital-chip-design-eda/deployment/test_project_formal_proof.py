from deployment.collateral_store import CollateralStore
from deployment.project_execution import prove_project_invariant


def test_project_formal_proof_preserves_bounded_solver_result(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    record = store.add("p1", "counter.sv", "rtl", "r7", "module counter(input clk); wire q; assign q = 1'b0; endmodule\n")
    result = prove_project_invariant(record, signal="q", expected_value="0", collateral_root=tmp_path / "collateral", run_root=tmp_path / "run")
    assert result["status"] == "passed"
    assert result["proof_result"] == "proven"
    assert result["claim"] == "bounded_formal_result"


def test_project_formal_counterexample_enters_common_triage_path(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "collateral")
    record = store.add("p1", "counter.sv", "rtl", "r7", "module counter(input clk); wire q; assign q = clk; endmodule\n")
    result = prove_project_invariant(record, signal="q", expected_value="0", collateral_root=tmp_path / "collateral", run_root=tmp_path / "run", sequence=1)
    assert result["status"] == "failed"
    assert result["proof_result"] == "counterexample"
    assert result["failure"]["signal"] == "q"
    assert (tmp_path / "run/verification-ir.json").is_file()
    assert '"failed"' in (tmp_path / "run/closure-report.json").read_text()
