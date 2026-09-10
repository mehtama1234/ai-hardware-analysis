import json, subprocess, sys
from pathlib import Path
def test_seeded_regblock_failure_is_localized():
    root = Path(__file__).parent
    assert subprocess.run([sys.executable, str(root/"run_benchmark.py")], capture_output=True).returncode == 0
    report = json.loads((root/"runs/latest/triage-report.json").read_text())
    assert report["status"] == "failed"
    assert report["failure"] == {"actual":"170","cycle":1,"expected":"0","signal":"reg0"}
    assert report["root_cause"]["marker"] == "SEEDED_BUG"
    assert (root / "runs/latest/generated_checks.sv").is_file()
    assert "REQ-REG-ADDRESS" in (root / "runs/latest/generated_checks.sv").read_text()
