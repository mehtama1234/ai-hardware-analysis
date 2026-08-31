#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "distributed-training-optimizer"))

from distributed_training_optimizer import build_distributed_training_optimizer_report  # noqa: E402


def main() -> None:
    report = build_distributed_training_optimizer_report()
    print(
        "wrote distributed-training-optimizer/distributed-training-optimizer-report.json and "
        "distributed-training-optimizer/reports/distributed-training-optimizer-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )


if __name__ == "__main__":
    main()
