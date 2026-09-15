import json
from pathlib import Path

import pytest

from verification_platform.diagnosis import build_balanced_diagnosis, write_balanced_diagnosis
from verification_platform.triage import Failure


def test_balanced_diagnosis_requires_both_sides_and_is_digest_bound(tmp_path: Path):
    diagnosis = build_balanced_diagnosis(
        Failure(1, "counter_q", "0", "1"),
        source_revision="counter-v1",
        for_evidence=["cycle 1 observed counter_q=1; specification expects 0"],
        against_evidence=["the RTL assignment is syntactically valid, but its dependency path omits enable"],
        causal_paths=[["counter_q", "rst"]],
    )
    record = diagnosis.record()
    assert record["status"] == "review_required"
    assert len(record["diagnosis_sha256"]) == 64
    path = write_balanced_diagnosis(diagnosis, tmp_path / "diagnosis.json")
    assert json.loads(path.read_text(encoding="utf-8"))["diagnosis_sha256"] == record["diagnosis_sha256"]


def test_balanced_diagnosis_rejects_missing_against_evidence():
    with pytest.raises(ValueError, match="FOR and AGAINST"):
        build_balanced_diagnosis(
            Failure(1, "q", "0", "1"),
            source_revision="v1",
            for_evidence=["observed mismatch"],
            against_evidence=[],
        )
