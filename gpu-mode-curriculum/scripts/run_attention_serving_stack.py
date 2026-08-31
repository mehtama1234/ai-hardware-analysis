#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "attention-serving-stack"))

from attention_serving_stack import build_attention_serving_report


def main() -> int:
    report = build_attention_serving_report()
    print(
        "wrote attention-serving-stack/attention-serving-report.json and "
        "attention-serving-stack/reports/attention-serving-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
