import pytest

from .coverage_closure import bound_coverage_snapshot, compare_coverage


def _snapshot(covered: int, *, revision: str = "r1", total: int = 10):
    return bound_coverage_snapshot(kind="functional", covered=covered, total=total, source_revision=revision, evidence_digest="a" * 64)


def test_coverage_comparison_records_delta_and_open_gaps():
    report = compare_coverage(_snapshot(4), _snapshot(7), required_source_revision="r1")
    assert report["status"] == "open"
    assert report["coverage_delta"] == 3
    assert report["gaps"][0]["missing"] == 3


def test_coverage_comparison_converges_only_at_same_scope():
    report = compare_coverage(_snapshot(9), _snapshot(10), required_source_revision="r1")
    assert report["status"] == "converged"
    assert report["gaps"] == []


def test_coverage_comparison_blocks_stale_revision_and_decrease():
    stale = compare_coverage(_snapshot(4), _snapshot(7, revision="r2"), required_source_revision="r1")
    decreased = compare_coverage(_snapshot(7), _snapshot(6), required_source_revision="r1")
    assert stale["status"] == "blocked"
    assert decreased["status"] == "blocked"


def test_coverage_snapshot_rejects_unbound_evidence():
    with pytest.raises(ValueError, match="evidence_digest"):
        bound_coverage_snapshot(kind="functional", covered=1, total=2, source_revision="r1", evidence_digest="short")
