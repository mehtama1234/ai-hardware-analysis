import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def test_approved_repair_retest_proves_closure():
    result = subprocess.run([sys.executable, str(ROOT / "retest_benchmark.py")], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((ROOT / "runs" / "retest" / "retest-report.json").read_text())
    assert report["status"] == "passed"
    assert report["repair"]["decision"] == "allowed"
    assert report["simulation_run"]["status"] == "passed"
    assert report["compile_run"]["status"] == "passed"
    assert (ROOT / "runs" / "retest" / "generated_checks.sv").is_file()
    assert (ROOT / "runs" / "retest" / "procedural_checks.sv").is_file()
    assert (ROOT / "runs" / "retest" / "uvm-counter-agent.sv").is_file()
    session = json.loads((ROOT / "runs" / "retest" / "session-ledger.json").read_text())
    assert [event["stage"] for event in session["events"]] == ["created", "planned", "executed", "triaged", "repair_review", "retested", "closed"]
    closure = json.loads((ROOT / "runs" / "retest" / "closure-report.json").read_text())
    assert {item["status"] for item in closure} == {"proven"}
    pov = json.loads((ROOT / "runs" / "retest" / "proof-of-value-report.json").read_text())
    assert pov["closure"]["proven"] == 3
    assert pov["coverage"]["percentage"] == 100.0
    assert pov["mixed_signal"]["claims"][1]["status"] == "unsupported"
    assert pov["requirements"]["planning_queue"][0]["requirement_id"] == "REQ-COUNTER-RESET"
    assert (ROOT / "counter.sv").read_text().count("SEEDED_BUG") == 1
    assert "if (enable)" in (ROOT / "runs" / "retest" / "counter_repaired.sv").read_text()


def test_single_end_to_end_entrypoint_reports_baseline_and_retest():
    result = subprocess.run([sys.executable, str(ROOT / "run_end_to_end.py")], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    summary = json.loads((ROOT / "runs" / "end-to-end-summary.json").read_text())
    assert summary["baseline"]["verification_status"] == "failed"
    assert summary["retest"]["verification_status"] == "passed"
    assert summary["formal"]["proof_result"] == "proven"
    assert summary["formal_counterexample"]["proof_result"] == "counterexample"
    assert summary["formal_counterexample"]["failure"]["actual"] == "1"
    assert len(summary["summary_sha256"]) == 64
    assert summary["artifact_manifest"] == "runs/artifact-manifest.json"
    assert summary["artifact_integrity"]["valid"] is True
    assert summary["pov_metrics"]["proven_delta"] == 3
    assert summary["pov_metrics"]["retest_coverage_percentage"] == 100.0
    assert (ROOT / "runs" / "artifact-manifest.json").is_file()
