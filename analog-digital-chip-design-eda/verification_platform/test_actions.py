from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.actions import recommend_next_action


def test_action_policy_prioritizes_failure_then_human_review():
    assert recommend_next_action({"triage": {"status": "failed"}})["action"] == "triage_failure"
    action = recommend_next_action({"requirements": {"unplanned": 1}, "execution": {"blocked": 0}})
    assert action == {"action": "review_unplanned_requirements", "reason": "requirements lack safe generated checks", "approval": "human_review"}


def test_action_policy_closes_only_when_no_gaps():
    assert recommend_next_action({"requirements": {"unplanned": 0}, "execution": {"blocked": 0}, "coverage": {"next_actions": []}})["approval"] == "human_signoff"
