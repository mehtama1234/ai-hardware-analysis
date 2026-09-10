from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.regression import run_regression, write_regression_report


def test_regression_collapses_duplicate_failures(tmp_path):
    jobs = [
        ("a", [sys.executable, "-c", "print('FAIL cycle=1 signal=q expected=0 actual=1')"]),
        ("b", [sys.executable, "-c", "print('FAIL cycle=9 signal=q expected=0 actual=1')"]),
        ("c", [sys.executable, "-c", "print('PASS')"]),
    ]
    report = run_regression(jobs, run_root=tmp_path, source_revision="r1")
    assert report["total_jobs"] == 3
    assert report["passed_jobs"] == 1
    assert report["failed_jobs"] == 2
    assert report["failure_count"] == 2
    assert report["cluster_count"] == 1
    output = write_regression_report(report, tmp_path / "regression.json")
    assert "report_sha256" in output.read_text(encoding="utf-8")
