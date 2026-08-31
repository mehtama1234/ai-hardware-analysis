#!/usr/bin/env python3
"""Build the reusable kernel autotuning database."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "autotune-db"))

from autotune_db import build_database, select_config  # noqa: E402
from autotune_db.builder import DB_JSON, REPORT_MD  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--select-family")
    parser.add_argument("--select-shape")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    database = build_database()
    if args.select_family:
        selected = select_config(database, args.select_family, args.select_shape)
        print(json.dumps(selected, indent=2, ensure_ascii=False))
    elif args.json:
        print(json.dumps(database, indent=2, ensure_ascii=False))
    else:
        print(f"wrote {DB_JSON.relative_to(ROOT)} and {REPORT_MD.relative_to(ROOT)} ({database['record_count']} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
