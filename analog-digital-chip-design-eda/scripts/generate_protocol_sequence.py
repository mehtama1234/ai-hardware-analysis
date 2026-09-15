#!/usr/bin/env python3
"""Generate a deterministic SystemVerilog sequence from protocol-plan-v1."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification_platform.protocol import load_protocol_plan, write_protocol_sequence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        plan = load_protocol_plan(args.plan)
        output = write_protocol_sequence(plan, args.output)
    except (OSError, ValueError):
        return 2
    print(f"generated {output} plan_sha256={plan.digest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
