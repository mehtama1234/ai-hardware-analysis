from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.coverage import parse_coverage, rank_coverage_gaps


def test_coverage_percentage_is_deterministic(tmp_path):
    path = tmp_path / "coverage.json"
    path.write_text('{"kind":"functional","covered":3,"total":4}', encoding="utf-8")
    result = parse_coverage(path, root=tmp_path)
    assert result.percentage == 75.0
    assert result.evidence_path == "coverage.json"


def test_invalid_coverage_is_rejected(tmp_path):
    path = tmp_path / "coverage.json"
    path.write_text('{"kind":"code","covered":5,"total":4}', encoding="utf-8")
    try:
        parse_coverage(path, root=tmp_path)
    except ValueError as exc:
        assert "coverage requires" in str(exc)
    else:
        raise AssertionError("invalid coverage must be rejected")


def test_coverage_gaps_rank_next_evidence_action():
    gaps = rank_coverage_gaps([
        {"kind": "assertion", "covered": 1, "total": 4},
        {"kind": "functional", "covered": 0, "total": 2},
        {"kind": "code", "covered": 3, "total": 3},
    ])
    assert [item["kind"] for item in gaps] == ["assertion", "functional"]
    assert gaps[0]["missing"] == 3
    assert "uncovered assertion" in gaps[0]["next_action"]
