import json
import hashlib

from deployment.signoff_service import create_signoff, verify_signoff, write_signoff


def test_signoff_binds_reviewer_to_report_digest(tmp_path):
    report = tmp_path / "proof-of-value-report.json"
    payload = {"status": "passed"}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    report.write_text(json.dumps({**payload, "report_sha256": digest}))
    review = create_signoff(report, reviewer="verification-lead", notes="inspect the failed baseline", approved=False)
    assert review["status"] == "review_required"
    signed = json.loads(write_signoff(report, reviewer="verification-lead", notes="approved for pilot record", approved=True).read_text())
    assert signed["status"] == "approved"
    assert signed["report_sha256"] == digest
    assert verify_signoff(tmp_path / "pilot-signoff.json") is True
    report.write_text(json.dumps({"report_sha256": "b" * 64}))
    assert verify_signoff(tmp_path / "pilot-signoff.json") is False
