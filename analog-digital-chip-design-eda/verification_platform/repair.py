"""Bounded repair proposals; applying changes remains outside this module."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .policy import Action, authorize
from .triage import Failure


@dataclass(frozen=True)
class RepairProposal:
    requirement_id: str
    file: str
    line: int
    before: str
    after: str
    rationale: str

    @property
    def action(self) -> Action:
        return Action("repair", self.rationale, changes_design_intent=True)

    def decision(self, *, human_approved: bool = False) -> str:
        return authorize(self.action, human_approved=human_approved)


def propose_enable_guard(failure: Failure, *, requirement_id: str, file: str, line: int) -> RepairProposal:
    """Create the known bounded repair for the seeded enable-gate defect."""
    if failure.signal != "counter_q" or failure.expected != "0":
        raise ValueError("enable-guard proposal only applies to the counter hold failure")
    return RepairProposal(requirement_id, file, line, "counter_q <= counter_q + 4'd1;", "if (enable) counter_q <= counter_q + 4'd1;", "guard counter increment with enable to satisfy the hold requirement")


def apply_to_copy(source: str | Path, destination: str | Path, proposal: RepairProposal, *, human_approved: bool = False) -> Path:
    """Apply an approved exact-text replacement to a separate file."""
    if proposal.decision(human_approved=human_approved) != "allowed":
        raise PermissionError("human approval is required before applying a repair")
    content = Path(source).read_text(encoding="utf-8")
    if content.count(proposal.before) != 1:
        raise ValueError("repair precondition must match exactly one source occurrence")
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content.replace(proposal.before, proposal.after, 1), encoding="utf-8")
    return output
