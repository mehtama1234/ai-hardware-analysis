#!/usr/bin/env python3
"""Record an explicit digest-bound human approval or rejection decision."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--decision", choices=("approve", "reject"), required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reviewer = args.reviewer.strip()
    scope = args.scope.strip()
    reason = args.reason.strip()
    if not reviewer or not scope or not reason:
        raise SystemExit("reviewer, scope, and reason must be non-empty")
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipt = {
        "schema_version": "flagship-human-review-receipt-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "human_approved" if args.decision == "approve" else "human_rejected",
        "approval": args.decision == "approve",
        "reviewer": reviewer,
        "decision": args.decision,
        "decision_scope": scope,
        "decision_reason": reason,
        "reviewed_manifest": {"path": str(manifest_path.relative_to(ROOT)), "sha256": manifest.get("manifest_sha256")},
        "reviewed_evidence_sha256": digest(manifest.get("evidence", [])),
        "decision_under_review": manifest.get("release_decision"),
        "claim_boundary": "Explicit human decision bound to the reviewed manifest and evidence list; this does not authorize unsupported physical, silicon, or production claims.",
    }
    receipt["receipt_sha256"] = digest(receipt)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "approval": receipt["approval"], "output": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
