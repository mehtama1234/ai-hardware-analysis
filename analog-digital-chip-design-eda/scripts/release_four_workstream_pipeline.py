#!/usr/bin/env python3
"""Promote a verified four-workstream checkpoint through human approval."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification_platform.workflow import promote_checkpoint_to_release


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--approval-note", required=True)
    parser.add_argument("--approve", action="store_true")
    args = parser.parse_args()
    try:
        result = promote_checkpoint_to_release(
            args.checkpoint, artifact_root=args.artifact_root, reviewer=args.reviewer,
            approval_note=args.approval_note, human_approved=args.approve,
        )
    except PermissionError as error:
        print(json.dumps({"status": "review_required", "error": str(error)}, sort_keys=True))
        return 2
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({"status": "blocked", "error": str(error)}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
