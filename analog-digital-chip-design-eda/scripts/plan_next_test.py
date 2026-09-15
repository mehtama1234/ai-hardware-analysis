#!/usr/bin/env python3
"""Emit a deterministic, reviewable next-test plan from coverage evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from verification_platform.closure_lab import propose_next_test


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("coverage", type=Path)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--evidence", action="append", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.coverage.read_text(encoding="utf-8"))
    plan = propose_next_test(payload, source_revision=args.source_revision, evidence=args.evidence)
    result = {"status": "complete", "plan": None if plan is None else plan.record()}
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
