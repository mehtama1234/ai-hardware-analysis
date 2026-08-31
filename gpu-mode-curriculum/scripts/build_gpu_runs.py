#!/usr/bin/env python3
"""Build the GPU-host run import report."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gpu-runs"))

from gpu_runs import build_gpu_runs  # noqa: E402


def main() -> None:
    report = build_gpu_runs()
    coverage = report["coverage"]
    print(
        "wrote gpu-runs/gpu-run-report.json and gpu-runs/reports/gpu-run-report.md "
        f"({coverage['run_count']} runs, {coverage['promotion_step_count']} promotion steps, status={report['status']})"
    )


if __name__ == "__main__":
    main()
