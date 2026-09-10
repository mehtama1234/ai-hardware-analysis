import json
from pathlib import Path
import subprocess
import sys


def test_seeded_fifo_failure_is_localized():
    root = Path(__file__).parent
    result = subprocess.run([sys.executable, str(root / "run_benchmark.py")], capture_output=True, text=True)
    assert result.returncode == 0
    report = json.loads((root / "runs/latest/triage-report.json").read_text())
    assert report["status"] == "failed"
    assert report["failure"] == {"actual": "3", "cycle": 3, "expected": "2", "signal": "count"}
    assert report["root_cause"]["marker"] == "SEEDED_BUG"
    assert (root / "runs/latest/generated_checks.sv").is_file()
    assert "REQ-FIFO-BOUNDS" in (root / "runs/latest/generated_checks.sv").read_text()
    assert (root / "runs/latest/waveform.vcd").is_file()
