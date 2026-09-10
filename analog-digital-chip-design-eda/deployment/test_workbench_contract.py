from pathlib import Path


WORKBENCH = Path(__file__).parents[1] / "site" / "verification-workbench.html"


def test_workbench_exposes_live_api_and_evidence_boundaries():
    html = WORKBENCH.read_text(encoding="utf-8")
    for endpoint in (
        "/v1/projects/",
        "/dashboard",
        "/collateral",
        "/v1/jobs",
        "/run-async",
        "/proof-of-value",
        "/bundle/download",
        "/compare/",
        "/signoff",
    ):
        assert endpoint in html
    assert "evidence-backed" in html
    assert "reference marker · not exhaustive coverage" in html.lower()
    assert "Proposal created as review-only" in html
    assert "confirm('Sign off this exact evidence package as reviewed?')" in html


def test_workbench_keeps_an_offline_demo_path():
    html = WORKBENCH.read_text(encoding="utf-8")
    assert "Demo data loaded" in html
    assert "Demo fallback · API unavailable" in html
    assert "Demo report: 3 blockers" in html
