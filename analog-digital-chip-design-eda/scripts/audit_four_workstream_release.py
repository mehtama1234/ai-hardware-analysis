#!/usr/bin/env python3
"""Audit a retained four-workstream run without promoting it to release."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification_platform.workflow import load_checkpoint, resume_checkpoint, verify_four_workstream_release_inputs


def audit(checkpoint_path: str | Path, artifact_root: str | Path) -> dict:
    checkpoint = load_checkpoint(checkpoint_path)
    resume = resume_checkpoint(checkpoint_path, artifact_root=artifact_root)
    semantic = verify_four_workstream_release_inputs(checkpoint, artifact_root=artifact_root)
    result_path = Path(artifact_root).resolve() / "four-workstream-result.json"
    result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else {}
    ready = (
        resume.get("status") == "ready"
        and resume.get("next_stage") == "release"
        and semantic.get("valid") is True
    )
    return {
        "schema_version": "four-workstream-release-audit-v1",
        "status": "ready_for_approval" if ready else "blocked",
        "workflow_id": checkpoint.workflow_id,
        "source_revision": checkpoint.source_revision,
        "pipeline_status": result.get("status"),
        "claim_status": result.get("claim_status"),
        "resume": resume,
        "semantic_release_inputs": semantic,
        "claim_boundary": "audit only; no release manifest is created and no human approval is inferred",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = audit(args.checkpoint, args.artifact_root)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        result = {
            "schema_version": "four-workstream-release-audit-v1",
            "status": "blocked",
            "error": str(error),
            "claim_boundary": "audit only; no release manifest is created and no human approval is inferred",
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ready_for_approval" else 1


if __name__ == "__main__":
    raise SystemExit(main())
