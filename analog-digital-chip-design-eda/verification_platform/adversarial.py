"""Deterministic skeptical review for model-generated verification proposals."""
from __future__ import annotations
from typing import Any
from .agent import AgentProposal

def review_proposal(proposal: AgentProposal, *, source_revision: str, evidence: list[str], signal: str, cycle: int) -> dict[str, Any]:
    issues: list[str] = []
    if proposal.source_revision != source_revision:
        issues.append("source revision is not current")
    if not set(proposal.evidence).issubset(set(evidence)):
        issues.append("proposal cites evidence outside the supplied scope")
    if proposal.status != "review_required":
        issues.append("proposal is not review-gated")
    if proposal.kind == "diagnosis" and (signal not in proposal.action or str(cycle) not in proposal.action):
        issues.append("diagnosis does not identify the failing signal and cycle")
    return {"accepted": not issues, "issues": issues, "judge": "deterministic-adversarial-v1"}
