"""Source-bound coverage comparison and convergence decisions."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .coverage import rank_coverage_gaps


def _digest(body: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _validate_snapshot(snapshot: dict[str, Any]) -> None:
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != "bound-coverage-snapshot-v1":
        raise ValueError("coverage snapshot schema is unsupported")
    if not isinstance(snapshot.get("kind"), str) or not snapshot["kind"]:
        raise ValueError("coverage snapshot requires kind")
    if not isinstance(snapshot.get("covered"), int) or not isinstance(snapshot.get("total"), int) or snapshot["total"] <= 0 or not 0 <= snapshot["covered"] <= snapshot["total"]:
        raise ValueError("coverage snapshot requires valid covered/total")
    if not isinstance(snapshot.get("source_revision"), str) or not snapshot["source_revision"]:
        raise ValueError("coverage snapshot requires source_revision")
    if not isinstance(snapshot.get("evidence_digest"), str) or len(snapshot["evidence_digest"]) != 64:
        raise ValueError("coverage snapshot requires a 64-character evidence_digest")


def bound_coverage_snapshot(*, kind: str, covered: int, total: int, source_revision: str, evidence_digest: str) -> dict[str, Any]:
    snapshot = {
        "schema_version": "bound-coverage-snapshot-v1",
        "kind": kind,
        "covered": covered,
        "total": total,
        "source_revision": source_revision,
        "evidence_digest": evidence_digest,
    }
    _validate_snapshot(snapshot)
    snapshot["snapshot_sha256"] = _digest(snapshot)
    return snapshot


def compare_coverage(before: dict[str, Any], after: dict[str, Any], *, required_source_revision: str) -> dict[str, Any]:
    """Compare coverage only when source, kind, and denominator are identical."""
    _validate_snapshot(before)
    _validate_snapshot(after)
    if not isinstance(required_source_revision, str) or not required_source_revision:
        raise ValueError("required_source_revision is required")
    same_scope = before["kind"] == after["kind"] and before["total"] == after["total"] and before["source_revision"] == after["source_revision"] == required_source_revision
    non_decreasing = after["covered"] >= before["covered"]
    complete = after["covered"] == after["total"]
    body = {
        "schema_version": "coverage-convergence-report-v1",
        "source_revision": required_source_revision,
        "before": before,
        "after": after,
        "same_scope": same_scope,
        "non_decreasing": non_decreasing,
        "coverage_delta": after["covered"] - before["covered"],
        "status": "converged" if same_scope and non_decreasing and complete else "open" if same_scope and non_decreasing else "blocked",
        "claim_boundary": "comparable coverage evidence for the declared kind and denominator; not proof of unreachable behavior absence",
    }
    if same_scope and non_decreasing and not complete:
        body["gaps"] = rank_coverage_gaps([after])
    else:
        body["gaps"] = []
    body["report_sha256"] = _digest(body)
    return body
