#!/usr/bin/env python3
"""Independently verify the review-gated LLM-to-repair handoff artifact."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", type=Path)
    parser.add_argument("--model-report", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()

    review = json.loads(args.review.read_text(encoding="utf-8"))
    model_report = json.loads(args.model_report.read_text(encoding="utf-8"))
    errors: list[str] = []
    if review.get("schema_version") not in {"llm-approved-counter-repair-v1", "llm-approved-counter-repair-v2"}:
        errors.append("unexpected repair review schema")
    if review.get("design_id") != "seeded_counter":
        errors.append("repair review is not for seeded_counter")
    source = review.get("source", {})
    repair = review.get("repair", {})
    if review.get("schema_version") == "llm-approved-counter-repair-v2" and repair.get("model_generated") is not True:
        errors.append("model-generated repair marker is missing")
    approval_status = review.get("approval", {}).get("status")
    if approval_status == "approved":
        if repair.get("decision") != "allowed":
            errors.append("approved repair must be allowed")
        if review.get("retest", {}).get("status") != "passed":
            errors.append("approved repair retest did not pass")
        if review.get("retest", {}).get("original_unchanged") is not True:
            errors.append("canonical source was changed")
        approval = review.get("approval", {})
        scope = review.get("verification_scope", {})
        if approval.get("proposal_sha256") != repair.get("model_repair_sha256"):
            errors.append("approval is not bound to the model proposal")
        if approval.get("source_sha256") != source.get("sha256"):
            errors.append("approval is not bound to the canonical source")
        if not scope or approval.get("scope_sha256") != scope.get("scope_sha256"):
            errors.append("approval is not bound to the verification scope")
        formal = review.get("retest", {}).get("formal", {})
        if formal.get("status") != "passed" or not formal.get("sha256"):
            errors.append("formal retest is missing or did not pass")
        if scope.get("scope_sha256") != object_digest({key: value for key, value in scope.items() if key != "scope_sha256"}):
            errors.append("verification scope digest is invalid")
    else:
        if repair.get("decision") != "review_required":
            errors.append("repair must remain review_required before approval")
        if approval_status not in {"required", "rejected"}:
            errors.append("review artifact must show approval required or rejected")
    if source.get("sha256") != digest(args.source):
        errors.append("canonical source hash changed or does not match review")
    rows = model_report.get("model_runs", {}).get("local-batch-command", [])
    row = next((item for item in rows if item.get("design_id") == "seeded_counter"), None)
    if row is None:
        errors.append("accepted seeded_counter model diagnosis is missing")
    elif not (
        row.get("status") == "available"
        and row.get("grounded") is True
        and row.get("diagnosis_match") is True
        and row.get("adversarial_review", {}).get("accepted") is True
    ):
        errors.append("seeded_counter model diagnosis is not accepted")
    if repair.get("before") != "counter_q <= counter_q + 4'd1;":
        errors.append("repair precondition is not the expected bounded change")
    if repair.get("after") != "if (enable) counter_q <= counter_q + 4'd1;":
        errors.append("repair replacement is not the expected bounded change")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(json.dumps({"status": "passed", "approval": approval_status, "canonical_source_unchanged": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
