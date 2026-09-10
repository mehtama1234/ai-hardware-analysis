import json, subprocess, sys
from pathlib import Path
def test_fifo_repair_retests_cleanly():
    root=Path(__file__).parent
    result=subprocess.run([sys.executable,str(root/"retest_benchmark.py")],capture_output=True,text=True)
    assert result.returncode == 0
    report=json.loads((root/"runs/retest/retest-report.json").read_text())
    assert report["status"] == "passed" and report["repair"]["decision"] == "allowed" and report["repair"]["original_unchanged"] is True
