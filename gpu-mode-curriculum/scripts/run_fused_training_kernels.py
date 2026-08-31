#!/usr/bin/env python3
"""Build the fused training kernel report."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "fused-training-kernels"))

from fused_training_kernels import build_fused_training_report


def main() -> None:
    report = build_fused_training_report()
    print(
        "wrote fused-training-kernels/fused-training-report.json and "
        "fused-training-kernels/reports/fused-training-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )


if __name__ == "__main__":
    main()
