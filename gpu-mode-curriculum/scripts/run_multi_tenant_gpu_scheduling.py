#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "multi-tenant-gpu-scheduling"))

from multi_tenant_gpu_scheduling import build_multi_tenant_scheduling_report


def main() -> int:
    report = build_multi_tenant_scheduling_report()
    print(
        "wrote multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json and "
        "multi-tenant-gpu-scheduling/reports/multi-tenant-scheduling-report.md "
        f"({report['policy_count']} policies, {report['tenant_count']} tenants, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
