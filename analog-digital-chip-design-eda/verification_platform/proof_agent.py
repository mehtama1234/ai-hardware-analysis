"""Bounded LLM trajectory for invariant and lemma proposals."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .agent_team import run_agent_team


def build_proof_agent_requests(*, property_id: str, source_revision: str, evidence: list[str], failure_context: str) -> list[dict[str, Any]]:
    if not property_id or not source_revision or not isinstance(evidence, list) or not evidence or not failure_context.strip():
        raise ValueError("property_id, source_revision, evidence, and failure_context are required")
    common = {"property_id": property_id, "task_id": property_id, "allowed_source_revision": source_revision, "evidence": list(evidence)}
    return [
        {**common, "role": "invariant_generator", "task": f"propose a candidate inductive lemma for {property_id}; context: {failure_context}"},
        {**common, "role": "reviewer", "task": f"identify assumptions and a reachability check for lemma {property_id}"},
    ]


def run_proof_agent(*, property_id: str, source_revision: str, evidence: list[str], failure_context: str, backend: str, output_root: str | Path | None = None) -> dict[str, Any]:
    requests = build_proof_agent_requests(property_id=property_id, source_revision=source_revision, evidence=evidence, failure_context=failure_context)
    team = run_agent_team(requests, backend=backend, source_revision=source_revision)
    result: dict[str, Any] = {
        "schema_version": "proof-agent-run-v1",
        "property_id": property_id,
        "source_revision": source_revision,
        "backend": backend,
        "team": team,
        "claim_boundary": "candidate lemma and assumption proposals only; formal proof remains independent",
    }
    result["run_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if output_root is not None:
        output = Path(output_root)
        output.mkdir(parents=True, exist_ok=True)
        (output / "proof-agent-run.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
