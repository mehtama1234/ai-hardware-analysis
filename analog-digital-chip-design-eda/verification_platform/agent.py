"""Provider-neutral, evidence-grounded envelope for LLM agent proposals."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

ALLOWED_KINDS = {"plan", "check", "diagnosis", "repair", "next_action", "lemma"}
ALLOWED_STATUSES = {"proposal", "review_required"}
FORBIDDEN_CLAIMS = {"passed", "proven", "closed", "production_ready", "customer_roi"}


@dataclass(frozen=True)
class AgentProposal:
    proposal_id: str
    kind: str
    source_revision: str
    action: str
    rationale: str
    evidence: tuple[str, ...]
    status: str = "proposal"

    @property
    def proposal_sha256(self) -> str:
        body = asdict(self)
        return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def record(self) -> dict[str, Any]:
        return {**asdict(self), "evidence": list(self.evidence), "proposal_sha256": self.proposal_sha256}


def validate_agent_proposal(payload: dict[str, Any]) -> AgentProposal:
    if not isinstance(payload, dict):
        raise ValueError("agent proposal must be an object")
    required = {"proposal_id", "kind", "source_revision", "action", "rationale", "evidence"}
    if not required.issubset(payload):
        raise ValueError("agent proposal is missing required fields")
    kind = payload["kind"]
    status = payload.get("status", "proposal")
    evidence = payload["evidence"]
    if kind not in ALLOWED_KINDS:
        raise ValueError("agent proposal kind is unsupported")
    if status not in ALLOWED_STATUSES:
        raise ValueError("agent proposal status must remain reviewable")
    if not isinstance(evidence, list) or not evidence or any(not isinstance(item, str) or not item.strip() for item in evidence):
        raise ValueError("agent proposal requires non-empty evidence references")
    for field in ("proposal_id", "source_revision", "action", "rationale"):
        if not isinstance(payload[field], str) or not payload[field].strip():
            raise ValueError(f"agent proposal {field} must be non-empty")
    forbidden = {str(value).lower() for value in payload.get("claims", []) if isinstance(payload.get("claims"), list)} & FORBIDDEN_CLAIMS
    if forbidden:
        raise ValueError(f"agent proposal cannot assert closure claims: {sorted(forbidden)}")
    return AgentProposal(payload["proposal_id"], kind, payload["source_revision"], payload["action"], payload["rationale"], tuple(evidence), status)
