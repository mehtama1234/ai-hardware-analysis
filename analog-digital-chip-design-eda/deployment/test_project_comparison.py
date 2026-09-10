import json

from deployment.project_comparison import compare_project_runs, write_comparison


def _write_run(root, status, covered):
    root.mkdir()
    (root / "project-simulation-result.json").write_text(json.dumps({"project_id": "p1", "status": status, "compile_run": {"tool": "iverilog", "status": "passed"}, "simulation_run": {"tool": "vvp", "status": status}}))
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
