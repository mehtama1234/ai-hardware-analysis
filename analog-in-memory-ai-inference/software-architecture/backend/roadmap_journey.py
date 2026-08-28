from copy import deepcopy
from pathlib import Path
import json


ROADMAP_JOURNEY_SCHEMA_VERSION = "roadmap_journey_demo.v1"
REQUIRED_STEP_FIELDS = {
    "title",
    "phase",
    "intro",
    "question",
    "evidence",
    "next",
    "primary",
    "secondary",
    "result",
    "missing",
    "artifact",
    "proof_level",
    "upstream_evidence",
    "downstream_claims",
    "depends_on_steps",
    "unlocks_steps",
}


def _journey_path():
    return Path(__file__).resolve().parent.parent / "roadmap-journey-demo.json"


def load_roadmap_journey(package_id=None):
    payload = json.loads(_journey_path().read_text())
    if payload.get("schema_version") != ROADMAP_JOURNEY_SCHEMA_VERSION:
        raise ValueError("Unexpected roadmap journey schema version.")
    steps = payload.get("steps")
    if not isinstance(steps, list) or len(steps) != 14:
        raise ValueError("Roadmap journey must contain exactly 14 steps.")
    for index, step in enumerate(steps, start=1):
        missing = REQUIRED_STEP_FIELDS - set(step)
        if missing:
            raise ValueError(f"Roadmap journey step {index} is missing fields: {sorted(missing)}")
        if not isinstance(step["upstream_evidence"], list) or not step["upstream_evidence"]:
            raise ValueError(f"Roadmap journey step {index} must list upstream evidence.")
        if not isinstance(step["downstream_claims"], list) or not step["downstream_claims"]:
            raise ValueError(f"Roadmap journey step {index} must list downstream claims.")
        if not isinstance(step["depends_on_steps"], list):
            raise ValueError(f"Roadmap journey step {index} must list dependency step numbers.")
        if not isinstance(step["unlocks_steps"], list):
            raise ValueError(f"Roadmap journey step {index} must list unlocked step numbers.")
        linked_steps = step["depends_on_steps"] + step["unlocks_steps"]
        if any(not isinstance(step_number, int) or step_number < 1 or step_number > 14 for step_number in linked_steps):
            raise ValueError(f"Roadmap journey step {index} has an invalid step link.")

    result = deepcopy(payload)
    result.update(
        {
            "result_type": "roadmap_journey",
            "source": "static_readability_contract",
            "package_id": package_id,
            "plain_reading": (
                "This endpoint returns the guided end-to-end roadmap journey used by the HTML page. "
                "It is a product contract for how the platform should explain evidence, gaps, and next work."
            ),
        }
    )
    return result
