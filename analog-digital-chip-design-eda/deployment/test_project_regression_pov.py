import json

from deployment.project_regression_pov import build_regression_pov, write_regression_pov


def test_regression_pov_aggregates_case_coverage(tmp_path):
    (tmp_path / "project-regression-result.json").write_text(json.dumps({"project_id": "p1", "rtl_artifact_id": "r1", "status": "failed", "case_count": 2, "passed_cases": 1, "failed_cases": 1, "cases": [{"status": "passed"}, {"status": "failed"}]}))
    for index, payload in enumerate(({"kind": "functional", "covered": 3, "total": 4}, {"kind": "functional", "covered": 1, "total": 4}), 1):
        case = tmp_path / f"case-{index:03d}"
        case.mkdir()
        (case / "functional-coverage.json").write_text(json.dumps(payload))
    report = build_regression_pov(tmp_path)
    assert report["coverage"]["covered"] == 4
    assert report["coverage"]["total"] == 8
    assert report["coverage"]["percentage"] == 50.0
    assert json.loads(write_regression_pov(tmp_path).read_text())["report_sha256"] == report["report_sha256"]
