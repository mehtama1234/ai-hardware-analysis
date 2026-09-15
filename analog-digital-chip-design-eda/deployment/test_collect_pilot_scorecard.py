import json
from pathlib import Path

import pytest

from scripts.collect_pilot_scorecard import collect
from deployment.pilot_scorecard import validate_scorecard


def _write(path: Path, *, offset: float = 0.0) -> None:
    categories = ["simulation", "lint", "formal", "regression"]
    rows = []
    for index in range(20):
        rows.append({"failure_id": f"f-{index}", "category": categories[index % 4], "triage_seconds": 10 + offset, "reproduction_seconds": 20 + offset, "manual_actions": 5 + offset, "root_cause_actionable": index % 5 != 0, "evidence_complete": True, "closure_integrity": index % 7 != 0, "blocked_or_timeout": index < 3})
    path.write_text(json.dumps(rows), encoding="utf-8")


def test_collect_pilot_scorecard_is_traceable(tmp_path: Path):
    baseline, workbench, output = (tmp_path / name for name in ("baseline.json", "workbench.json", "scorecard.json"))
    _write(baseline, offset=5); _write(workbench)
    scorecard = collect(baseline, workbench, output=output, customer="demo", project="block")
    assert not validate_scorecard(scorecard)
    assert scorecard["pilot"]["sample_size"] == 20
    assert scorecard["pilot"]["blocked_or_timeout_count"] == 3
    assert len(scorecard["evidence_sha256"]) == 2
    assert len(scorecard["metrics"][0]["workbench_confidence_95"]) == 2
    assert len(scorecard["metrics"][0]["baseline_confidence_95"]) == 2
    assert len(scorecard["metrics"][1]["workbench_confidence_95"]) == 2


def test_collect_rejects_unmatched_samples(tmp_path: Path):
    baseline, workbench, output = (tmp_path / name for name in ("baseline.json", "workbench.json", "scorecard.json"))
    _write(baseline); _write(workbench)
    rows = json.loads(workbench.read_text()); rows[-1]["failure_id"] = "different"; workbench.write_text(json.dumps(rows))
    with pytest.raises(ValueError, match="same failure IDs"):
        collect(baseline, workbench, output=output, customer="demo", project="block")


def test_collect_rejects_invalid_observation_values(tmp_path: Path):
    baseline, workbench, output = (tmp_path / name for name in ("baseline.json", "workbench.json", "scorecard.json"))
    _write(baseline); _write(workbench)
    rows = json.loads(workbench.read_text()); rows[0]["triage_seconds"] = -1; workbench.write_text(json.dumps(rows))
    with pytest.raises(ValueError, match="invalid triage_seconds"):
        collect(baseline, workbench, output=output, customer="demo", project="block")
