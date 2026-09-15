from pathlib import Path


def test_time_zero_matrix_classifies_all_checked_in_cases(tmp_path: Path):
    from scripts.run_time_zero_regression_matrix import run_matrix

    report = run_matrix(tmp_path / "matrix", timeout_seconds=0.2)
    assert report["status"] == "passed"
    assert len(report["cases"]) == 5
    assert all(item["passed_expectation"] for item in report["cases"].values())
