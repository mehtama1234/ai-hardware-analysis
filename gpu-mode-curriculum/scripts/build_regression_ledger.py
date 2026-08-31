#!/usr/bin/env python3
"""Build the performance regression ledger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "regression-ledger"))

from regression_ledger import build_ledger  # noqa: E402
from regression_ledger.builder import LEDGER_JSON, REPORT_MD  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    ledger = build_ledger()
    if args.json:
        print(json.dumps(ledger, indent=2, ensure_ascii=False))
    else:
        print(
            f"wrote {LEDGER_JSON.relative_to(ROOT)} and {REPORT_MD.relative_to(ROOT)} "
            f"({ledger['metric_count']} metrics, {ledger['failed']} failed)"
        )
    return 0 if ledger["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
