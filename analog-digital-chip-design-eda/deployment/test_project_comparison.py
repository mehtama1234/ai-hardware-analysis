import json

from deployment.project_comparison import compare_project_runs, write_comparison


def _write_run(root, status, covered, rtl="rtl-a", testbench="tb-a"):
    root.mkdir()
    (root / "project-simulation-result.json").write_text(json.dumps({"project_id": "p1", "status": status, "rtl_artifact_id": rtl, "testbench_artifact_id": testbench, "compile_run": {"tool": "iverilog", "status": "passed"}, "simulation_run": {"tool": "vvp", "status": status}}))
    (root / "closure-report.json").write_text("[]")
    if status == "failed":
        (root / "diagnosis.json").write_text(json.dumps({"status": "review_required"}))


def test_compare_project_runs_reports_resolution_and_coverage_delta(tmp_path):
    baseline, retest = tmp_path / "baseline", tmp_path / "retest"
    _write_run(baseline, "failed", 0)
    _write_run(retest, "passed", 1)
    comparison = compare_project_runs(baseline, retest)
    assert comparison["metrics"]["failure_resolved"] is True
    assert comparison["metrics"]["coverage_delta_percentage_points"] == 100.0
    assert json.loads(write_comparison(baseline, retest).read_text())["comparison_sha256"] == comparison["comparison_sha256"]

def test_compare_project_runs_marks_narrow_scope_incomparable(tmp_path):
    baseline, retest = tmp_path / "baseline", tmp_path / "retest"
    _write_run(baseline, "failed", 0, testbench="tb-full")
    _write_run(retest, "passed", 1, testbench="tb-smoke")
    comparison = compare_project_runs(baseline, retest)
    assert comparison["metrics"]["scope_comparable"] is False
    assert comparison["metrics"]["failure_resolved"] is None
    assert comparison["metrics"]["coverage_delta_percentage_points"] is None
    assert "incomparable" in comparison["claim_boundary"]
