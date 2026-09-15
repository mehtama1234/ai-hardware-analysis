import json
from hashlib import sha256

from scripts.verify_customer_pilot_packet import verify_packet
from deployment.signoff_service import write_signoff


def test_customer_packet_fails_closed_for_open_readiness(tmp_path):
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps({"schema_version": "verification-production-readiness-v1", "customer_production_ready": False}), encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(json.dumps({"schema_version": "verification-pilot-scorecard-v1", "metrics": [], "pilot": {}}), encoding="utf-8")
    result = verify_packet(readiness_path=readiness, scorecard_path=scorecard, root=tmp_path)
    assert result["verified"] is False
    assert "customer production readiness is not true" in result["errors"]
    assert "customer pilot packet requires a signoff receipt" in result["errors"]


def test_customer_packet_rejects_review_only_or_mismatched_signoff(tmp_path):
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps({"schema_version": "verification-production-readiness-v1", "customer_production_ready": False}), encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(json.dumps({"schema_version": "verification-pilot-scorecard-v1", "metrics": [], "pilot": {}}), encoding="utf-8")
    report = tmp_path / "other.json"
    report_payload = {"report": "other"}
    report_payload["report_sha256"] = sha256(json.dumps({"report": "other"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    report.write_text(json.dumps(report_payload), encoding="utf-8")
    signoff = tmp_path / "signoff.json"
    signoff.write_text(json.dumps({"status": "review_required", "report_path": str(report), "report_sha256": report_payload["report_sha256"]}), encoding="utf-8")
    result = verify_packet(readiness_path=readiness, scorecard_path=scorecard, root=tmp_path, signoff_path=signoff)
    assert "signoff receipt must have approved status" in result["errors"]
    assert "signoff receipt is bound to a different scorecard" in result["errors"]


def test_customer_packet_accepts_matching_approved_scorecard(tmp_path):
    evidence = tmp_path / "observations.json"
    evidence.write_text("[]\n", encoding="utf-8")
    evidence_digest = sha256(evidence.read_bytes()).hexdigest()
    metrics = []
    for name, unit in [("triage_latency", "seconds"), ("root_cause_usefulness", "fraction"), ("reproduction_time", "seconds"), ("evidence_completeness", "fraction"), ("manual_effort", "actions"), ("closure_integrity", "fraction")]:
        metrics.append({"name": name, "unit": unit, "baseline_median": 10, "baseline_confidence_95": [9, 11], "workbench_median": 7, "workbench_confidence_95": [6, 8], "evidence": ["observations.json"]})
    scorecard_payload = {"schema_version": "verification-pilot-scorecard-v1", "pilot": {"sample_size": 20}, "metrics": metrics, "evidence_sha256": {"observations.json": evidence_digest}, "review": {"lead_reviewer": "lead", "receipt_sha256": "a" * 64}}
    scorecard_payload["scorecard_sha256"] = sha256(json.dumps(scorecard_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(json.dumps(scorecard_payload), encoding="utf-8")
    signoff = write_signoff(scorecard, reviewer="lead", notes="approved", approved=True)
    checklist = tmp_path / "checklist.md"
    checklist.write_text("controls\n", encoding="utf-8")
    readiness = tmp_path / "readiness.json"
    readiness_payload = {"schema_version": "verification-production-readiness-v1", "customer_production_ready": True, "pilot_controls_verified": True, "open_count": 0, "open_controls": [], "control_count": 1, "verified_count": 1, "checklist": "checklist.md", "checklist_sha256": sha256(checklist.read_bytes()).hexdigest()}
    readiness_payload["readiness_sha256"] = sha256(json.dumps(readiness_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    readiness.write_text(json.dumps(readiness_payload), encoding="utf-8")
    signoff.unlink()
    signoff = write_signoff(scorecard, reviewer="lead", notes="approved", approved=True, reviewer_subject="oidc|lead")
    result = verify_packet(readiness_path=readiness, scorecard_path=scorecard, root=tmp_path, signoff_path=signoff)
    assert result["verified"] is True, result["errors"]


def test_customer_packet_rejects_inconsistent_ready_report(tmp_path):
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps({"schema_version": "verification-production-readiness-v1", "customer_production_ready": True, "open_count": 2, "open_controls": ["missing"], "control_count": 3, "verified_count": 3}), encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text("{}", encoding="utf-8")
    result = verify_packet(readiness_path=readiness, scorecard_path=scorecard, root=tmp_path)
    assert "readiness report still contains open controls" in result["errors"]


def test_customer_packet_rejects_boolean_readiness_counts(tmp_path):
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps({"schema_version": "verification-production-readiness-v1", "customer_production_ready": True, "open_count": False, "open_controls": [], "control_count": True, "verified_count": True}), encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text("{}", encoding="utf-8")
    result = verify_packet(readiness_path=readiness, scorecard_path=scorecard, root=tmp_path)
    assert "readiness report still contains open controls" in result["errors"]
    assert "readiness control counts do not show complete verification" in result["errors"]


def test_customer_packet_rejects_null_open_controls(tmp_path):
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps({"schema_version": "verification-production-readiness-v1", "customer_production_ready": True, "open_count": 0, "open_controls": None, "control_count": 1, "verified_count": 1}), encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text("{}", encoding="utf-8")
    result = verify_packet(readiness_path=readiness, scorecard_path=scorecard, root=tmp_path)
    assert "readiness report still contains open controls" in result["errors"]


def test_customer_packet_rejects_zero_control_report(tmp_path):
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps({"schema_version": "verification-production-readiness-v1", "customer_production_ready": True, "open_count": 0, "open_controls": [], "control_count": 0, "verified_count": 0}), encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text("{}", encoding="utf-8")
    result = verify_packet(readiness_path=readiness, scorecard_path=scorecard, root=tmp_path)
    assert "readiness control counts do not show complete verification" in result["errors"]


def test_customer_packet_rejects_stale_readiness_checklist_digest(tmp_path):
    checklist = tmp_path / "checklist.md"
    checklist.write_text("controls\n", encoding="utf-8")
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps({"schema_version": "verification-production-readiness-v1", "customer_production_ready": True, "open_count": 0, "open_controls": [], "control_count": 1, "verified_count": 1, "checklist": "checklist.md", "checklist_sha256": "0" * 64}), encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text("{}", encoding="utf-8")
    result = verify_packet(readiness_path=readiness, scorecard_path=scorecard, root=tmp_path)
    assert "readiness checklist digest does not match" in result["errors"]


def test_customer_packet_rejects_inputs_outside_root(tmp_path):
    outside = tmp_path.parent / "outside-readiness.json"
    outside.write_text(json.dumps({"schema_version": "verification-production-readiness-v1", "customer_production_ready": True}), encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text("{}", encoding="utf-8")
    result = verify_packet(readiness_path=outside, scorecard_path=scorecard, root=tmp_path)
    assert "readiness report is outside packet root" in result["errors"]


def test_customer_packet_rejects_signoff_outside_root(tmp_path):
    readiness = tmp_path / "readiness.json"
    readiness.write_text(json.dumps({"schema_version": "verification-production-readiness-v1", "customer_production_ready": True}), encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text("{}", encoding="utf-8")
    outside = tmp_path.parent / "outside-signoff.json"
    outside.write_text("{}", encoding="utf-8")
    result = verify_packet(readiness_path=readiness, scorecard_path=scorecard, root=tmp_path, signoff_path=outside)
    assert "signoff receipt is outside packet root" in result["errors"]
