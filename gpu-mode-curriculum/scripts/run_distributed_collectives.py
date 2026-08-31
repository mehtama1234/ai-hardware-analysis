#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "distributed-collectives"))

from distributed_collectives import build_distributed_collectives_report


def main() -> int:
    report = build_distributed_collectives_report()
    print(
        "wrote distributed-collectives/distributed-collectives-report.json and "
        "distributed-collectives/reports/distributed-collectives-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
