#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "numerical-reproducibility"))

from numerical_reproducibility import build_numerical_reproducibility_report


def main() -> int:
    report = build_numerical_reproducibility_report()
    print(
        "wrote numerical-reproducibility/numerical-reproducibility-report.json and "
        "numerical-reproducibility/reports/numerical-reproducibility-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
