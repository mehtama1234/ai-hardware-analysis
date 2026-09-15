import json
from pathlib import Path

from scripts.validate_usability_study import validate


ROOT = Path(__file__).resolve().parents[1]


def test_draft_template_is_valid():
    payload = json.loads((ROOT / "deployment" / "pilot-usability-study-template.json").read_text())
    assert validate(payload) == []


def test_finalized_results_cannot_claim_completion_without_observations():
    payload = json.loads((ROOT / "deployment" / "pilot-usability-study-template.json").read_text())
    errors = validate(payload, finalized=True)
    assert any("at least three participants" in error for error in errors)
    assert any("lead_reviewer" in error for error in errors)
