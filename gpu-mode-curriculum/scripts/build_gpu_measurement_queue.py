#!/usr/bin/env python3
"""Build the GPU measurement queue."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gpu-measurement-queue"))

from gpu_measurement_queue import build_measurement_queue  # noqa: E402


def main() -> None:
    report = build_measurement_queue()
    print(
        "wrote gpu-measurement-queue/gpu-measurement-queue.json and "
        "gpu-measurement-queue/reports/gpu-measurement-queue.md "
        f"({report['status']}, {report['measured_task_count']}/{report['task_count']} measured)"
    )


if __name__ == "__main__":
    main()
