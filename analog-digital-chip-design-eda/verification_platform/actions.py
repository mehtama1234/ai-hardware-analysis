"""Bounded next-action policy for verification agents."""

from __future__ import annotations

from typing import Any


def recommend_next_action(report: dict[str, Any]) -> dict[str, str]:
    """Choose the highest-priority evidence-producing action from a PoV report."""
    triage = report.get("triage", {})
    if triage.get("status") == "failed":
        return {"action": "triage_failure", "reason": "failure evidence requires diagnosis before closure", "approval": "not_required"}
    execution = report.get("execution", {})
    if execution.get("blocked", 0):
        return {"action": "restore_tool_backend", "reason": "blocked tool runs prevent valid closure", "approval": "not_required"}
    requirements = report.get("requirements", {})
    if requirements.get("unplanned", 0):
        return {"action": "review_unplanned_requirements", "reason": "requirements lack safe generated checks", "approval": "human_review"}
    coverage = report.get("coverage", {})
    if coverage.get("next_actions"):
        return {"action": "target_coverage_gap", "reason": "coverage remains incomplete", "approval": "not_required"}
    return {"action": "close_requirements", "reason": "no higher-priority evidence gap is reported", "approval": "human_signoff"}
