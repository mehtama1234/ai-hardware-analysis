#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hardware-capacity-planning"))

from hardware_capacity_planning import build_hardware_capacity_plan


def main() -> int:
    plan = build_hardware_capacity_plan()
    print(
        "wrote hardware-capacity-planning/hardware-capacity-plan.json and "
        "hardware-capacity-planning/reports/hardware-capacity-plan.md "
        f"({plan['profile_count']} profiles, {plan['workload_count']} workloads)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
