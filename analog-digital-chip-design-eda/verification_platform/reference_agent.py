"""Deterministic reference agent used when no external LLM provider is configured."""

from __future__ import annotations

from .agent import AgentProposal, validate_agent_proposal
from .triage import Failure


def propose_failure_diagnosis(
    failure: Failure,
    *,
    source_revision: str,
    evidence: list[str],
    dependency_cone: list[str] | None = None,
) -> AgentProposal:
    """Create a reviewable diagnosis proposal without asserting root cause or closure."""
    cone = [signal for signal in (dependency_cone or []) if signal.strip()]
    focus = ", ".join(cone) if cone else failure.signal
    return validate_agent_proposal({
        "proposal_id": f"diagnosis-{failure.signal}-{failure.cycle}",
        "kind": "diagnosis",
        "source_revision": source_revision,
        "action": f"inspect {focus} at cycle {failure.cycle}",
        "rationale": (
            f"Observed {failure.signal}={failure.actual}, expected {failure.expected}, "
            f"at cycle {failure.cycle}; this is a hypothesis requiring human review and retest."
        ),
        "evidence": evidence,
        "status": "review_required",
    })
