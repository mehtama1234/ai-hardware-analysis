#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "persistent-kernels"))

from persistent_kernels import build_persistent_kernel_report


def main() -> int:
    report = build_persistent_kernel_report()
    print(
        "wrote persistent-kernels/persistent-kernels-report.json and "
        "persistent-kernels/reports/persistent-kernels-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
