#!/usr/bin/env python3
"""Build the GPUMODE capstone acceptance report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "capstone-acceptance"))

from capstone_acceptance import build_acceptance  # noqa: E402
from capstone_acceptance.evaluator import REPORT_JSON, REPORT_MD  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = build_acceptance()
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            f"wrote {REPORT_JSON.relative_to(ROOT)} and {REPORT_MD.relative_to(ROOT)} "
            f"({report['score']}/{report['max_score']} points, {report['status']})"
        )
    return 0 if report["failed_criteria"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
