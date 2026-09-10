"""Human-gated, exact-match repair proposals for customer collateral."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RepairProposal:
    artifact_id: str
    before_sha256: str
    before: str
    after: str
    rationale: str
    occurrences: int

    def review(self, *, approved: bool) -> dict[str, Any]:
        return {**asdict(self), "status": "allowed" if approved and self.occurrences == 1 else "review_required"}


def propose_repair(record: dict[str, Any], *, collateral_root: str | Path, before: str, after: str, rationale: str, approved: bool = False) -> tuple[dict[str, Any], str | None]:
    source = Path(collateral_root) / str(record["path"])
    content = source.read_text(encoding="utf-8")
    occurrences = content.count(before)
    if not before or not after or not rationale or occurrences != 1:
        proposal = RepairProposal(record["id"], hashlib.sha256(content.encode()).hexdigest(), before, after, rationale, occurrences)
        return proposal.review(approved=approved), None
    proposal = RepairProposal(record["id"], hashlib.sha256(content.encode()).hexdigest(), before, after, rationale, occurrences)
    review = proposal.review(approved=approved)
    if review["status"] != "allowed":
        return review, None
    return review, content.replace(before, after, 1)
