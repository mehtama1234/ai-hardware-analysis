from verification_platform.closure_lab import propose_next_test


def test_next_test_targets_largest_gap_and_is_reviewable():
    plan = propose_next_test(
        [
            {"kind": "assertion", "covered": 2, "total": 5},
            {"kind": "branch", "covered": 1, "total": 2},
        ],
        source_revision="design-v1",
        evidence=["latest/functional-coverage.json"],
    )
    assert plan is not None
    assert plan.target_kind == "assertion"
    assert plan.proposal.status == "review_required"
    assert plan.proposal.source_revision == "design-v1"
    assert plan.record()["plan_sha256"] == plan.plan_sha256


def test_next_test_returns_none_when_coverage_is_complete():
    assert propose_next_test({"kind": "functional", "covered": 3, "total": 3}, source_revision="r", evidence=["coverage.json"]) is None
