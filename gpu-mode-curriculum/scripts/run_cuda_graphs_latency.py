#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cuda-graphs-latency"))

from cuda_graphs_latency import build_cuda_graphs_latency_report


def main() -> int:
    report = build_cuda_graphs_latency_report()
    print(
        "wrote cuda-graphs-latency/cuda-graphs-latency-report.json and "
        "cuda-graphs-latency/reports/cuda-graphs-latency-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
