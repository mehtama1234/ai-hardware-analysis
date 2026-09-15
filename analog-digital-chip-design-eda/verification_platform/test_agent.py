import pytest

from verification_platform.agent import validate_agent_proposal


def test_agent_proposal_is_evidence_bound_and_reviewable():
    proposal = validate_agent_proposal({
        "proposal_id": "diag-1", "kind": "diagnosis", "source_revision": "rtl-abc",
        "action": "inspect counter_q cone", "rationale": "first divergence is cycle 1",
        "evidence": ["triage-report.json", "waveform.vcd"],
    })
    assert proposal.status == "proposal"
    assert len(proposal.proposal_sha256) == 64
    assert proposal.record()["evidence"] == ["triage-report.json", "waveform.vcd"]


def test_agent_proposal_rejects_unbounded_closure_claim():
    with pytest.raises(ValueError, match="closure claims"):
        validate_agent_proposal({
            "proposal_id": "bad", "kind": "diagnosis", "source_revision": "rtl",
            "action": "close run", "rationale": "looks good", "evidence": ["report.json"],
            "claims": ["proven"],
        })


def test_agent_proposal_rejects_missing_evidence():
    with pytest.raises(ValueError, match="evidence references"):
        validate_agent_proposal({
            "proposal_id": "bad", "kind": "repair", "source_revision": "rtl",
            "action": "change source", "rationale": "fix bug", "evidence": [],
        })
