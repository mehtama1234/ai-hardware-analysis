from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.pov import build_pov_report, verify_pov_digest, write_pov_report


def test_pov_report_is_explicit_and_hashed(tmp_path):
    (tmp_path / "specification-ir.json").write_text(json.dumps({"requirements": [{"id": "REQ-1"}]}), encoding="utf-8")
    (tmp_path / "verification-plan.json").write_text(json.dumps([{"id": "CHECK-1"}]), encoding="utf-8")
    (tmp_path / "closure-report.json").write_text(json.dumps([{"status": "failed"}]), encoding="utf-8")
    (tmp_path / "triage-report.json").write_text(json.dumps({"status": "failed", "first_divergence": {}, "root_cause": {}}), encoding="utf-8")
    (tmp_path / "tool-capabilities.json").write_text(json.dumps([{"tool": "iverilog", "status": "available"}, {"tool": "sby", "status": "blocked"}]), encoding="utf-8")
    (tmp_path / "verification-ir.json").write_text(json.dumps({"tool_runs": [{"tool": "iverilog", "status": "passed"}, {"tool": "vvp", "status": "failed"}, {"tool": "yosys-sat", "status": "passed", "metadata": {"proof_result": "counterexample"}}]}), encoding="utf-8")
    report = build_pov_report(tmp_path)
    assert report["requirements"] == {"total": 1, "planned_checks": 1, "unplanned": 0, "planning_queue": []}
    assert report["closure"]["failed"] == 1
    assert report["coverage"]["next_actions"] == []
    assert report["toolchain"]["available"] == 1
    assert report["toolchain"]["blocked"] == 1
    assert report["execution"] == {"tool_runs": 3, "passed": 2, "failed": 1, "blocked": 0, "duration_seconds": 0, "tools": ["iverilog", "vvp", "yosys-sat"], "proof_results": {"proven": 0, "counterexample": 1, "unknown": 0}}
    assert report["generation"]["emitted_count"] == 0
    assert report["generation"]["sha256"] == {}
    assert report["artifact_integrity"]["valid"] is False
    assert report["next_action"]["action"] == "triage_failure"
    assert len(report["report_sha256"]) == 64
    assert verify_pov_digest(report)
    report["closure"]["failed"] = 0
    assert not verify_pov_digest(report)
    assert write_pov_report(tmp_path).is_file()
