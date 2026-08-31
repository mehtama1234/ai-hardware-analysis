#!/usr/bin/env python3
"""Build distributed topology and parallelism planning report."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "distributed-topology"))

from distributed_topology import build_distributed_topology_plan  # noqa: E402


def main() -> int:
    report = build_distributed_topology_plan()
    print(
        "wrote distributed-topology/distributed-topology-plan.json and "
        "distributed-topology/reports/distributed-topology-plan.md "
        f"({report['topology_count']} topologies, {report['workload_count']} workloads, status={report['status']})"
    )
    return 0 if report["status"] == "topology-plan-ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
