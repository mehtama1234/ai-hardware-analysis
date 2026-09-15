import json
from pathlib import Path

from scripts.check_seeded_agent_causal_closure import validate


def test_causal_closure_checker_accepts_verified_report(tmp_path: Path):
    report = {"schema_version": "seeded-agent-repair-closure-report-v3", "task_count": 16, "passed_tasks": 16, "tasks": [], "status": "passed"}
    report["report_sha256"] = __import__("hashlib").sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    errors = validate(report)
    assert "causal repair closure must contain 16 passing tasks" in errors
    assert "causal repair closure metrics do not report complete 16-task closure" in errors


def test_causal_closure_checker_rejects_tampered_report():
    report = {"schema_version": "seeded-agent-repair-closure-report-v3", "task_count": 16, "passed_tasks": 16, "tasks": [], "status": "passed", "report_sha256": "0" * 64}
    assert "causal repair closure must contain 16 passing tasks" in validate(report)
    assert "report_sha256 mismatch" in validate(report)
