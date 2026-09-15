"""Bounded repair proposals; applying changes remains outside this module."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from .policy import Action, authorize
from .triage import Failure
from .runner import run_command

EDIT_OPERATORS = {"exact_text_replace"}

def build_repair_patch_candidate(
    payload: dict[str, object],
    source: str | Path,
    *,
    source_revision: str,
    evidence: list[str] | tuple[str, ...],
    allowed_source_locations: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Validate an agent-proposed exact-text patch without applying it."""
    if not source_revision or not isinstance(payload, dict):
        raise ValueError("repair payload and source_revision are required")
    source_path = Path(source).resolve()
    if not source_path.is_file():
        raise ValueError("repair candidate source must exist")
    before, after = payload.get("before"), payload.get("after")
    if not isinstance(before, str) or not isinstance(after, str) or not before or before == after:
        raise ValueError("repair candidate requires distinct non-empty before and after text")
    declared_file = payload.get("file")
    if declared_file is not None and Path(str(declared_file)).resolve() != source_path:
        raise ValueError("repair candidate file is outside the validated source")
    declared_hash = payload.get("source_sha256")
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    if declared_hash is not None and declared_hash != source_hash:
        raise ValueError("repair candidate source digest does not match")
    text = source_path.read_text(encoding="utf-8")
    if text.count(before) != 1:
        raise ValueError("repair candidate before text must match exactly one source occurrence")
    line = text[:text.index(before)].count("\n") + 1
    if allowed_source_locations is not None:
        allowed_lines = {
            int(item["line"])
            for item in allowed_source_locations
            if isinstance(item, dict)
            and isinstance(item.get("line"), int)
            and Path(str(item.get("file", source_path))).resolve() == source_path
        }
        if line not in allowed_lines:
            raise ValueError("repair candidate line is not a ranked causal root-cause location")
    if not isinstance(evidence, (list, tuple)) or not evidence or any(not isinstance(item, str) or not item.strip() for item in evidence):
        raise ValueError("repair candidate requires non-empty evidence")
    edit_operator = payload.get("edit_operator", "exact_text_replace")
    if not isinstance(edit_operator, str) or edit_operator not in EDIT_OPERATORS:
        raise ValueError("repair candidate edit_operator is unsupported")
    result: dict[str, object] = {
        "schema_version": "repair-patch-candidate-v1",
        "status": "review_required",
        "proposal_id": str(payload.get("proposal_id", "")),
        "requirement_id": str(payload.get("requirement_id", "")),
        "edit_operator": edit_operator,
        "source_revision": source_revision,
        "source": str(source_path),
        "source_sha256": source_hash,
        "line": line,
        "root_cause_location_bound": allowed_source_locations is not None,
        "before": before,
        "after": after,
        "evidence": list(evidence),
        "claim_boundary": "exact-text patch candidate only; no source mutation, repair approval, retest, or closure claim",
    }
    result["candidate_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


@dataclass(frozen=True)
class RepairProposal:
    requirement_id: str
    file: str
    line: int
    before: str
    after: str
    rationale: str
    edit_operator: str = "exact_text_replace"

    @property
    def action(self) -> Action:
        return Action("repair", self.rationale, changes_design_intent=True)

    def decision(self, *, human_approved: bool = False) -> str:
        if self.edit_operator not in EDIT_OPERATORS:
            return "review_required"
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


def run_approved_repair_retest(
    source: str | Path,
    destination: str | Path,
    proposal: RepairProposal,
    command: list[str],
    *,
    run_root: str | Path,
    source_revision: str,
    expected_artifacts: list[str] | None = None,
    timeout_seconds: float = 60.0,
    human_approved: bool = False,
) -> dict[str, object]:
    """Apply a bounded repair to a copy and rerun the identical verification scope.

    The command must contain the source path exactly once.  The retest replaces
    that occurrence with the repaired copy, preserving every other command
    argument.  The result is a hash-bound record and never writes the canonical
    source file.
    """
    if not source_revision:
        raise ValueError("source_revision is required")
    if not command:
        raise ValueError("command is required")
    source_path = Path(source)
    destination_path = Path(destination)
    source_token = str(source_path)
    if command.count(source_token) != 1:
        raise ValueError("command must contain the source path exactly once")
    before_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    apply_to_copy(source_path, destination_path, proposal, human_approved=human_approved)
    repaired_hash = hashlib.sha256(destination_path.read_bytes()).hexdigest()
    retest_command = [str(destination_path) if argument == source_token else argument for argument in command]
    tool_run = run_command(
        retest_command,
        tool="repair-retest",
        run_root=run_root,
        source_revision=source_revision,
        timeout_seconds=timeout_seconds,
        expected_artifacts=expected_artifacts,
        run_id="approved-repair",
    )
    after_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    original_source_unchanged = before_hash == after_hash
    retest_status = "passed" if tool_run.status == "passed" and original_source_unchanged else "blocked"
    result: dict[str, object] = {
        "schema_version": "approved-repair-retest-v1",
        "source_revision": source_revision,
        "status": retest_status,
        "human_approved": human_approved,
        "proposal": asdict(proposal),
        "edit_operator": proposal.edit_operator,
        "source": str(source_path),
        "destination": str(destination_path),
        "original_source_sha256": before_hash,
        "repaired_source_sha256": repaired_hash,
        "original_source_unchanged": original_source_unchanged,
        "command": retest_command,
        "tool_run": asdict(tool_run),
    }
    if not original_source_unchanged:
        result["blocked_reason"] = "canonical source changed during repair retest"
    elif tool_run.status != "passed":
        result["blocked_reason"] = "repair retest command did not pass"
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    output = Path(run_root) / "repair-retest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
