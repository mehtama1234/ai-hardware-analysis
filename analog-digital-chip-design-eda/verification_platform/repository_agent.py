"""Repository-scale agent trajectory assembly over the shared agent contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .agent_team import run_agent_team
from .repair import build_repair_patch_candidate


def build_repository_agent_requests(*, task_id: str, source_revision: str, evidence: list[str], failure_context: str, repair_before: str | None = None, repair_after: str | None = None) -> list[dict[str, Any]]:
    """Create bounded role requests for one repository failure."""
    if not task_id or not source_revision or not isinstance(evidence, list) or not evidence or not failure_context.strip():
        raise ValueError("task_id, source_revision, evidence, and failure_context are required")
    if (repair_before is None) != (repair_after is None):
        raise ValueError("repair_before and repair_after must be supplied together")
    common = {"task_id": task_id, "allowed_source_revision": source_revision, "evidence": list(evidence)}
    repair_fields = ({"repair_before": repair_before, "repair_after": repair_after} if repair_before is not None else {})
    return [
        {**common, "role": "diagnostician", "task": f"localize the repository failure for task {task_id}; context: {failure_context}"},
        {**common, "role": "reviewer", "task": f"propose the next discriminating executable check for task {task_id}"},
        {**common, **repair_fields, "role": "repair_proposer", "task": f"propose a minimal review-only repair for task {task_id}"},
        {**common, "role": "reviewer", "task": f"review the diagnosis and repair evidence for task {task_id} without declaring closure"},
    ]


def run_repository_agent(*, task_id: str, source_revision: str, evidence: list[str], failure_context: str, backend: str, max_handoffs: int = 3, output_root: str | Path | None = None, repair_before: str | None = None, repair_after: str | None = None, repair_source: str | Path | None = None, allowed_source_locations: list[dict[str, object]] | None = None) -> dict[str, Any]:
    """Run the bounded repository trajectory and bind it to the task."""
    requests = build_repository_agent_requests(task_id=task_id, source_revision=source_revision, evidence=evidence, failure_context=failure_context, repair_before=repair_before, repair_after=repair_after)
    team = run_agent_team(requests, backend=backend, source_revision=source_revision, max_handoffs=max_handoffs)
    result: dict[str, Any] = {
        "schema_version": "repository-agent-run-v1",
        "task_id": task_id,
        "source_revision": source_revision,
        "backend": backend,
        "team": team,
        "claim_boundary": "bounded repository agent trajectory; proposals are review-only and do not prove repair or verification closure",
    }
    if repair_source is not None:
        repair_results = [item for item in team["results"] if item.get("role") == "repair_proposer" and item.get("grounded") is True]
        if not repair_results or "bounded_repair" not in repair_results[0]:
            result["patch_candidate_status"] = "blocked"
            result["patch_candidate_error"] = "no validated bounded repair handoff is available"
        else:
            bounded = repair_results[0]["bounded_repair"]
            try:
                result["patch_candidate"] = build_repair_patch_candidate(
                    {**bounded, "proposal_id": repair_results[0]["proposal"]["proposal_id"]},
                    repair_source, source_revision=source_revision, evidence=evidence,
                    allowed_source_locations=allowed_source_locations,
                )
            except (OSError, TypeError, ValueError) as error:
                result["patch_candidate_status"] = "blocked"
                result["patch_candidate_error"] = str(error)
    result["run_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if output_root is not None:
        output = Path(output_root)
        output.mkdir(parents=True, exist_ok=True)
        (output / "repository-agent-run.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
