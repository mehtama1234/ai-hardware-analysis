import json,subprocess,sys
from pathlib import Path
def test_handshake_failure_and_repair():
    root=Path(__file__).parent
    assert subprocess.run([sys.executable,str(root/"run_benchmark.py")],capture_output=True).returncode==0
    assert json.loads((root/"runs/latest/triage-report.json").read_text())["status"]=="failed"
    assert subprocess.run([sys.executable,str(root/"retest_benchmark.py")],capture_output=True).returncode==0
    report=json.loads((root/"runs/retest/retest-report.json").read_text())
    assert report["status"]=="passed" and report["repair"]["original_unchanged"] is True
