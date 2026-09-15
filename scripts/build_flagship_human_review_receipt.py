#!/usr/bin/env python3
"""Create an explicit, digest-bound pending human-review receipt."""
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
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evidence = manifest.get("evidence", [])
    receipt = {
        "schema_version": "flagship-human-review-receipt-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending_human_review",
        "approval": False,
        "reviewer": None,
        "reviewed_manifest": {"path": str(manifest_path.relative_to(ROOT)), "sha256": manifest.get("manifest_sha256")},
        "reviewed_evidence_sha256": digest(evidence),
        "decision_under_review": manifest.get("release_decision"),
        "required_decision": "approve_or_reject_with_named_reviewer_and_scope",
        "reason": "The package is evidence-complete for its declared local boundaries but remains blocked for held-out model generalization, physical/measured gates, and production controls.",
        "claim_boundary": "This is a pending review record, not human approval, release authorization, silicon signoff, or production signoff.",
    }
    receipt["receipt_sha256"] = digest(receipt)
    output = args.output.resolve(); output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "output": str(output), "approval": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
