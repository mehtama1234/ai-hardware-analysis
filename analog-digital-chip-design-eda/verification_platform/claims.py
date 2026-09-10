"""Domain-aware claim gates for the mixed-signal case study."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ClaimDomain = Literal["software", "simulation", "physical_layout", "measured_hardware"]


@dataclass(frozen=True)
class Claim:
    text: str
    domain: ClaimDomain
    evidence_kinds: tuple[str, ...]


def claim_status(claim: Claim, observed_evidence_kinds: set[str]) -> str:
    """Accept a claim only when every declared evidence kind is present."""
    if not claim.text or not claim.evidence_kinds:
        raise ValueError("claim text and evidence kinds are required")
    missing = set(claim.evidence_kinds) - observed_evidence_kinds
    return "proven" if not missing else "unsupported"
