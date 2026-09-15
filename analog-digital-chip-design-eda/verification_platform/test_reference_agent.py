from verification_platform.reference_agent import propose_failure_diagnosis
from verification_platform.triage import Failure


def test_reference_agent_emits_reviewable_failure_diagnosis():
    proposal = propose_failure_diagnosis(
        Failure(1, "counter_q", "0", "1"),
        source_revision="rtl-abc",
        evidence=["triage-report.json", "waveform.vcd"],
        dependency_cone=["counter_q", "enable"],
    )
    record = proposal.record()
    assert record["kind"] == "diagnosis"
    assert record["status"] == "review_required"
    assert record["source_revision"] == "rtl-abc"
    assert "counter_q, enable" in record["action"]
    assert "hypothesis" in record["rationale"]
    assert "proven" not in record
