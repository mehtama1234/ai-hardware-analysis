#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "moe-routing-all-to-all"))

from moe_routing_all_to_all import build_moe_routing_report


def main() -> int:
    report = build_moe_routing_report()
    print(
        "wrote moe-routing-all-to-all/moe-routing-report.json and "
        "moe-routing-all-to-all/reports/moe-routing-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
