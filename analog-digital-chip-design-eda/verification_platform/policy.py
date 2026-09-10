"""Human-approval gates for agent-proposed verification actions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Decision = Literal["allowed", "review_required", "denied"]


@dataclass(frozen=True)
class Action:
    kind: str
    description: str
    changes_design_intent: bool = False
    changes_closure: bool = False


def authorize(action: Action, *, human_approved: bool = False) -> Decision:
    """Require explicit human approval for intent or closure changes."""
    if not action.kind or not action.description:
        raise ValueError("action kind and description are required")
    if action.changes_design_intent or action.changes_closure:
        return "allowed" if human_approved else "review_required"
    return "allowed"
