from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.policy import Action, authorize


def test_design_change_requires_human_approval():
    action = Action("repair", "change enable guard", changes_design_intent=True)
    assert authorize(action) == "review_required"
    assert authorize(action, human_approved=True) == "allowed"


def test_read_only_analysis_is_allowed():
    assert authorize(Action("triage", "cluster failures")) == "allowed"
