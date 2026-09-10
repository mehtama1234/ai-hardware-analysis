import json

from deployment.project_pov import build_project_pov, write_project_pov


def test_project_pov_preserves_failed_closure_and_claim_boundary(tmp_path):
    (tmp_path / "project-simulation-result.json").write_text(json.dumps({"project_id": "p1", "rtl_artifact_id": "r1", "testbench_artifact_id": "t1", "status": "failed", "failure": {"signal": "q"}, "compile_run": {"tool": "iverilog", "status": "passed"}, "simulation_run": {"tool": "vvp", "status": "passed"}}))
    (tmp_path / "closure-report.json").write_text(json.dumps([{"requirement_id": "FAIL-q-1", "status": "failed"}]))
    (tmp_path / "diagnosis.json").write_text(json.dumps({"status": "review_required"}))
    report = build_project_pov(tmp_path)
    assert report["closure"]["failed"] == 1
    assert report["coverage"]["percentage"] == 0.0
    assert "measured-hardware" in report["claim_boundary"]
    assert report["report_sha256"]
    assert json.loads(write_project_pov(tmp_path).read_text())["report_sha256"] == report["report_sha256"]
