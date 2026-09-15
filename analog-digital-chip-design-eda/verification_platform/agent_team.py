"""Bounded multi-agent handoffs over the common proposal contract."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import time
from typing import Any

from .agent import AgentProposal
from .llm_backend import BackendResult, invoke_local_backend, invoke_openai_compatible_backend


ROLE_KINDS = {
    "specification_planner": "plan",
    "assertion_generator": "check",
    "diagnostician": "diagnosis",
    "repair_proposer": "repair",
    "reviewer": "next_action",
    "invariant_generator": "lemma",
}


def run_agent_team(
    requests: list[dict[str, Any]],
    *,
    backend: str,
    source_revision: str,
    max_handoffs: int = 3,
) -> dict[str, Any]:
    """Run a deterministic sequence of bounded, review-only agent roles.

    Each request must provide ``role``, ``task``, ``allowed_source_revision``,
    and non-empty ``evidence``.  Later roles receive only the most recent
    validated proposal records, not unrestricted prior prompts or raw model
    output.  This is orchestration evidence, not multi-agent correctness.
    """
    if not requests or backend not in {"local", "openai_compatible"} or not source_revision:
        raise ValueError("requests, supported backend, and source_revision are required")
    if max_handoffs < 0:
        raise ValueError("max_handoffs must be nonnegative")
    handoffs: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    for index, request in enumerate(requests):
        role = request.get("role")
        task = request.get("task")
        allowed = request.get("allowed_source_revision")
        evidence = request.get("evidence")
        if role not in ROLE_KINDS:
            results.append({"index": index, "status": "blocked", "error": "unsupported team role"})
            continue
        if not isinstance(task, str) or not task or allowed != source_revision or not isinstance(evidence, list) or not evidence:
            results.append({"index": index, "role": role, "status": "blocked", "error": "request is missing task, matching source revision, or evidence"})
            continue
        enriched = dict(request)
        # Bind the role's expected proposal kind into the backend request so
        # repository-specific roles cannot be silently interpreted as generic
        # diagnosis by a model transport.
        enriched["expected_kind"] = ROLE_KINDS[role]
        enriched["team_handoffs"] = handoffs[-max_handoffs:] if max_handoffs else []
        started = time.monotonic()
        backend_result: BackendResult = invoke_local_backend(enriched) if backend == "local" else invoke_openai_compatible_backend(enriched)
        record: dict[str, Any] = {"index": index, "role": role, "task": task, "backend": backend_result.backend, "status": backend_result.status, "error": backend_result.error, "duration_seconds": round(time.monotonic() - started, 6)}
        proposal = backend_result.proposal
        if proposal is not None:
            repair_choices_ok = True
            raw = backend_result.raw or {}
            if isinstance(raw, dict) and "_model_generated_fields" in raw:
                record["model_generated_fields"] = raw["_model_generated_fields"]
                record["request_bound_fields"] = raw.get("_request_bound_fields", [])
                if "_model_selected_repair" in raw:
                    record["model_selected_repair"] = raw["_model_selected_repair"]
            if role == "repair_proposer" and isinstance(request.get("repair_before"), str) and isinstance(request.get("repair_after"), str):
                if isinstance(raw.get("repair_choice"), str):
                    # The bounded-choice transport lets a model select the
                    # declared repair without reproducing long source text.
                    # Only the declared option is admissible; the adapter
                    # binds its exact before/after text below.
                    repair_choices_ok = raw.get("repair_choice") == "declared_repair"
                else:
                    # Preserve the original exact-text contract for existing
                    # one-shot and fixture backends.
                    repair_choices_ok = raw.get("before") == request["repair_before"] and raw.get("after") == request["repair_after"]
            grounded = (
                proposal.source_revision == source_revision
                and proposal.kind == ROLE_KINDS[role]
                and set(proposal.evidence).issubset(set(evidence))
                and proposal.status in {"proposal", "review_required"}
                and repair_choices_ok
            )
            record["proposal"] = proposal.record()
            record["grounded"] = grounded
            if grounded and role == "repair_proposer" and isinstance(request.get("repair_before"), str) and isinstance(request.get("repair_after"), str):
                record["bounded_repair"] = {"edit_operator": "exact_text_replace", "before": request["repair_before"], "after": request["repair_after"]}
            if not grounded:
                record["status"] = "blocked"
                record["error"] = "proposal failed team role, revision, evidence, repair-choice, or review-status gate"
            else:
                handoff = {"role": role, "proposal_id": proposal.proposal_id, "kind": proposal.kind, "action": proposal.action, "rationale": proposal.rationale, "evidence": list(proposal.evidence), "proposal_sha256": proposal.proposal_sha256}
                if "bounded_repair" in record:
                    handoff["bounded_repair"] = record["bounded_repair"]
                handoffs.append(handoff)
        results.append(record)
    result: dict[str, Any] = {
        "schema_version": "agent-team-run-v1",
        "backend": backend,
        "source_revision": source_revision,
        "roles": [request.get("role") for request in requests],
        "results": results,
        "handoffs": handoffs,
        "status": "available" if len(results) == len(requests) and all(item.get("status") == "available" for item in results) else "blocked",
        "claim_boundary": "bounded multi-agent evidence handoffs; proposals remain review-only and do not prove verification closure",
    }
    result["team_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result
