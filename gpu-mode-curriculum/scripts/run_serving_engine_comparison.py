#!/usr/bin/env python3
"""Build serving engine comparison report from serving trace replay metrics."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "serving-engine-comparison"))

from serving_engine_comparison import build_engine_comparison  # noqa: E402


def main() -> int:
    report = build_engine_comparison()
    print(
        "wrote serving-engine-comparison/serving-engine-comparison.json and "
        "serving-engine-comparison/reports/serving-engine-comparison.md "
        f"({report['engine_count']} engines, {report['scenario_count']} scenarios, status={report['status']})"
    )
    return 0 if report["status"] == "comparison-ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
