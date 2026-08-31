#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "parallel-primitives"))

from parallel_primitives import build_parallel_primitives_report


def main() -> int:
    report = build_parallel_primitives_report()
    print(
        "wrote parallel-primitives/parallel-primitives-report.json and "
        "parallel-primitives/reports/parallel-primitives-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
