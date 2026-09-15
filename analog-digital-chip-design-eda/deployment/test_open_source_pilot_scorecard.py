import json
from pathlib import Path

from deployment.pilot_scorecard import validate_scorecard
from scripts.build_open_source_pilot_scorecard import build_scorecard


def test_open_source_scorecard_only_populates_measurable_evidence(tmp_path: Path):
    run = tmp_path / "run"
    run.mkdir()
    (run / "pilot-summary.json").write_text(json.dumps({"design_count": 2, "passed_retests": 2, "metrics": {"all_artifacts_verified": True, "diagnosis_evidence_complete": 2}}), encoding="utf-8")
    for name in ("session-ledger.json", "pilot-release-manifest.json"):
        (run / name).write_text("{}", encoding="utf-8")
    scorecard = build_scorecard(run)
    assert not validate_scorecard(scorecard)
    assert scorecard["pilot"]["sample_size"] == 2
    assert scorecard["metrics"][0]["workbench_median"] is None
    assert scorecard["metrics"][3]["workbench_median"] == 1.0
    assert scorecard["review"]["lead_reviewer"] == ""
    assert len(scorecard["evidence_sha256"]) == 3
    assert all(len(digest) == 64 for digest in scorecard["evidence_sha256"].values())
    assert len(scorecard["scorecard_sha256"]) == 64
    tampered = dict(scorecard); tampered["pilot"] = dict(scorecard["pilot"], sample_size=99)
    assert "scorecard_sha256 does not match scorecard content" in validate_scorecard(tampered)
