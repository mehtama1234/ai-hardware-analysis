"""Fail-closed contracts for bounded versus inductive formal closure."""

from __future__ import annotations

import hashlib
import json
from typing import Any


_STATUSES = {"proven", "counterexample", "unknown", "blocked"}


def _digest(body: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_assumption_audit(
    assumptions: list[dict[str, Any]],
    reachability_results: list[dict[str, Any]],
    *,
    source_revision: str,
) -> dict[str, Any]:
    """Create a typed, evidence-backed audit for proof assumptions.

    A proof may use assumptions, but it may not silently treat an untested or
    stale assumption as established.  Each assumption therefore needs one
    matching solver reachability result whose source revision agrees and whose
    result digest is intact.  ``reachable`` is intentionally the only passing
    result; unknown and bounded-unreachable results remain blocked.
    """
    if not source_revision or not isinstance(assumptions, list) or not isinstance(reachability_results, list):
        raise ValueError("assumptions, reachability_results, and source_revision are required")
    results_by_id = {
        str(item.get("assumption_id")): item
        for item in reachability_results
        if isinstance(item, dict) and item.get("assumption_id")
    }
    checks: list[dict[str, Any]] = []
    for assumption in assumptions:
        assumption_id = str(assumption.get("id", "")) if isinstance(assumption, dict) else ""
        formula = assumption.get("formula") if isinstance(assumption, dict) else None
        result = results_by_id.get(assumption_id)
        check: dict[str, Any] = {"assumption_id": assumption_id, "formula": formula, "status": "blocked"}
        if not assumption_id or not isinstance(formula, str) or not formula.strip():
            check["reason"] = "assumption requires a non-empty id and formula"
        elif result is None:
            check["reason"] = "no solver reachability result matches assumption"
        else:
            body = {key: value for key, value in result.items() if key != "result_sha256"}
            digest_ok = result.get("result_sha256") == _digest(body)
            revision_ok = result.get("source_revision") == source_revision
            status_ok = result.get("status") == "reachable"
            check.update({"result_sha256": result.get("result_sha256"), "digest_valid": digest_ok, "source_revision_valid": revision_ok, "reachable": status_ok})
            if digest_ok and revision_ok and status_ok:
                check["status"] = "passed"
            else:
                check["reason"] = "solver evidence is stale, tampered, or not reachable"
        checks.append(check)
    audit: dict[str, Any] = {
        "schema_version": "assumption-audit-v1",
        "status": "passed" if checks and all(item["status"] == "passed" for item in checks) else "blocked",
        "source_revision": source_revision,
        "assumption_count": len(assumptions),
        "checks": checks,
        "claim_boundary": "solver-backed bounded reachability audit for declared assumptions; not a proof of the assumptions in all environments",
    }
    audit["audit_sha256"] = _digest(audit)
    return audit


def evaluate_proof_closure(
    *,
    property_id: str,
    source_revision: str,
    bounded_status: str,
    inductive_status: str,
    assumptions: list[dict[str, Any]],
    assumption_audit: dict[str, Any],
    reachable_state_status: str,
    vacuity_status: str,
    counterexample: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify proof evidence without allowing bounded-only closure."""
    if not isinstance(property_id, str) or not property_id or not isinstance(source_revision, str) or not source_revision:
        raise ValueError("property_id and source_revision are required")
    if bounded_status not in _STATUSES or inductive_status not in _STATUSES:
        raise ValueError("bounded and inductive statuses are unsupported")
    if not isinstance(assumptions, list) or any(not isinstance(item, dict) for item in assumptions):
        raise ValueError("assumptions must be a list of records")
    if not isinstance(assumption_audit, dict) or assumption_audit.get("status") not in {"passed", "blocked"}:
        raise ValueError("assumption audit must be passed or blocked")
    if assumption_audit.get("schema_version") != "assumption-audit-v1" or assumption_audit.get("source_revision") != source_revision:
        raise ValueError("assumption audit must be typed and bound to source_revision")
    audit_body = {key: value for key, value in assumption_audit.items() if key != "audit_sha256"}
    if assumption_audit.get("audit_sha256") != _digest(audit_body):
        raise ValueError("assumption audit digest does not match")
    if reachable_state_status not in {"passed", "blocked", "unknown"} or vacuity_status not in {"active", "vacuous", "unknown"}:
        raise ValueError("reachable-state and vacuity statuses are unsupported")
    bounded_only = bounded_status == "proven" and inductive_status != "proven"
    assumption_ok = assumption_audit["status"] == "passed" and bool(assumptions) and assumption_audit.get("assumption_count") == len(assumptions) and all(item.get("status") == "passed" for item in assumption_audit.get("checks", []))
    reachable_ok = reachable_state_status == "passed"
    vacuity_ok = vacuity_status == "active"
    proof_status = "proven" if bounded_status == "proven" and inductive_status == "proven" and assumption_ok and reachable_ok and vacuity_ok else "blocked"
    body: dict[str, Any] = {
        "schema_version": "formal-proof-closure-v1",
        "property_id": property_id,
        "source_revision": source_revision,
        "bounded_status": bounded_status,
        "inductive_status": inductive_status,
        "bounded_only": bounded_only,
        "assumptions": assumptions,
        "assumption_audit": assumption_audit,
        "reachable_state_status": reachable_state_status,
        "vacuity_status": vacuity_status,
        "proof_status": proof_status,
        "counterexample": counterexample,
        "claim_boundary": "inductive status is proven only for the declared model, assumptions, and solver evidence; no general silicon correctness claim",
    }
    body["result_sha256"] = _digest(body)
    return body
