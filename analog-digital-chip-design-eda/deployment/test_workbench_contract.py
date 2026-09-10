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
        "/repair-retest",
    ):
        assert endpoint in html
    assert "evidence-backed" in html
    assert 'data-tab="formal"' in html
    assert "Counterexample" in html
    for job_kind in ("project-simulation", "project-compile", "project-lint", "project-formal", "project-formal-proof", "project-regression"):
        assert job_kind in html
    assert "reference marker · not exhaustive coverage" in html.lower()
    assert "Proposal created as review-only" in html
    assert "approved:false" in html
    assert "approved:true" in html
    assert "confirm('Sign off this exact evidence package as reviewed?')" in html


def test_workbench_keeps_an_offline_demo_path():
    html = WORKBENCH.read_text(encoding="utf-8")
    assert "Demo data loaded" in html
    assert "Demo fallback · API unavailable" in html
    assert "Demo report: 3 blockers" in html
    assert "Stale · retrying" in html
    assert "Unauthorized · reconnect required" in html
    assert "setInterval" in html
    assert "Loading durable runs" in html
    assert "Loading project collateral" in html
