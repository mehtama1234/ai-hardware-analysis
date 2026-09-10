import json
from pathlib import Path
import subprocess
import sys


def test_multi_design_pilot_has_two_independent_failures():
    root = Path(__file__).parent
    result = subprocess.run([sys.executable, str(root / "run_pilot.py")], capture_output=True, text=True)
    assert result.returncode == 0
    summary = json.loads((root / "runs/latest/pilot-summary.json").read_text())
    assert summary["design_count"] == 5
    assert summary["failed_designs"] == 5
    assert summary["passed_retests"] == 5
    assert {item["repair_decision"] for item in summary["results"]} == {"allowed"}
    assert summary["metrics"]["original_sources_unchanged"] == 5
    assert summary["metrics"]["requirements_planned"] == 13
    assert summary["metrics"]["repair_success_rate_percent"] == 100.0
    assert summary["metrics"]["formal_readiness"]["passed"] == 1
    assert summary["metrics"]["next_actions"]["triage_failure"] == 5
    assert all(item["retest_next_action"]["action"] == "review_closure" for item in summary["results"])
    assert {item["design"] for item in summary["results"]} == {"seeded_counter", "seeded_fifo", "seeded_regblock", "register_peripheral", "seeded_handshake"}
    assert summary["summary_sha256"]
