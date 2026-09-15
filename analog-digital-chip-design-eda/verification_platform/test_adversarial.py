from verification_platform.adversarial import review_proposal
from verification_platform.agent import validate_agent_proposal

def test_adversarial_review_accepts_grounded_diagnosis():
    p = validate_agent_proposal({"proposal_id":"p","kind":"diagnosis","source_revision":"r","action":"inspect fault_signal_1 at cycle 7","rationale":"hypothesis","evidence":["e://1"],"status":"review_required"})
    assert review_proposal(p, source_revision="r", evidence=["e://1"], signal="fault_signal_1", cycle=7)["accepted"]

def test_adversarial_review_rejects_scope_escape():
    p = validate_agent_proposal({"proposal_id":"p","kind":"diagnosis","source_revision":"old","action":"inspect other at cycle 7","rationale":"hypothesis","evidence":["e://other"],"status":"review_required"})
    result = review_proposal(p, source_revision="r", evidence=["e://1"], signal="fault_signal_1", cycle=7)
    assert not result["accepted"] and len(result["issues"]) == 3
