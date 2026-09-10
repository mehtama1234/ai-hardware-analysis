import json

from deployment.signoff_service import create_signoff, write_signoff


def test_signoff_binds_reviewer_to_report_digest(tmp_path):
    report = tmp_path / "proof-of-value-report.json"
    report.write_text(json.dumps({"report_sha256": "a" * 64}))
    review = create_signoff(report, reviewer="verification-lead", notes="inspect the failed baseline", approved=False)
    assert review["status"] == "review_required"
    signed = json.loads(write_signoff(report, reviewer="verification-lead", notes="approved for pilot record", approved=True).read_text())
    assert signed["status"] == "approved"
    assert signed["report_sha256"] == "a" * 64
