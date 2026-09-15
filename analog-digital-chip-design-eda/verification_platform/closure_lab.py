"""Deterministic coverage-gap to next-test planning for the closure lab.

This module deliberately stops at a reviewable proposal.  It does not claim
that a generated test is sufficient or that coverage has been closed; a
subsequent executable run must produce new evidence at the same scope.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any, Iterable

from .agent import AgentProposal, validate_agent_proposal
from .coverage import CoverageResult, rank_coverage_gaps


@dataclass(frozen=True)
class NextTestPlan:
    test_id: str
    target_kind: str
    covered_before: int
    total_before: int
    expected_artifact: str
    proposal: AgentProposal

    @property
    def plan_sha256(self) -> str:
        body = asdict(self)
        body["proposal"] = self.proposal.record()
        return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def record(self) -> dict[str, Any]:
        return {**asdict(self), "proposal": self.proposal.record(), "plan_sha256": self.plan_sha256}


def propose_next_test(
    coverage: CoverageResult | dict[str, Any] | Iterable[CoverageResult | dict[str, Any]],
    *,
    source_revision: str,
    evidence: list[str],
    context: str = "",
) -> NextTestPlan | None:
    """Create the highest-priority executable test proposal for a gap.

    The returned proposal is always ``review_required`` and carries the
    source revision plus evidence references.  ``None`` means all supplied
    coverage dimensions are complete.
    """
    if isinstance(coverage, (CoverageResult, dict)):
        items = [coverage]
    else:
        items = list(coverage)
    gaps = rank_coverage_gaps(items)
    if not gaps:
        return None
    gap = gaps[0]
    slug = re.sub(r"[^a-z0-9]+", "-", gap["kind"].lower()).strip("-") or "coverage"
    test_id = f"next-{slug}-{gap['covered']}-of-{gap['total']}"
    artifact = f"next-tests/{test_id}/run-report.json"
    refs = list(evidence)
    if not refs:
        raise ValueError("next-test proposal requires evidence references")
    rationale = (
        f"Target {gap['missing']} uncovered {gap['kind']} item(s) ({gap['covered']}/{gap['total']} covered) "
        "with a bounded executable test; rerun at identical scope and inspect the resulting artifact."
    )
    if context.strip():
        rationale += f" Context: {context.strip()}"
    proposal = validate_agent_proposal({
        "proposal_id": test_id,
        "kind": "next_action",
        "source_revision": source_revision,
        "action": f"execute targeted {gap['kind']} test {test_id}",
        "rationale": rationale,
        "evidence": refs,
        "status": "review_required",
    })
    return NextTestPlan(test_id, gap["kind"], gap["covered"], gap["total"], artifact, proposal)

