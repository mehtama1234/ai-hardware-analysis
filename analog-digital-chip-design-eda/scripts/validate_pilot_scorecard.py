#!/usr/bin/env python3
"""Validate a verification pilot scorecard before handoff."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from deployment.pilot_scorecard import validate_scorecard


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scorecard", type=Path)
    parser.add_argument("--finalized", action="store_true", help="require complete pilot evidence and lead receipt")
    args = parser.parse_args()
    try:
        scorecard = json.loads(args.scorecard.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"invalid scorecard: {error}", file=sys.stderr)
        return 2
    errors = validate_scorecard(scorecard, finalized=args.finalized)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"valid scorecard: {args.scorecard}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
