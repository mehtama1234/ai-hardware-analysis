#!/usr/bin/env python3
"""Build GPU evidence provenance report."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gpu-provenance"))

from gpu_provenance import build_gpu_provenance  # noqa: E402


def main() -> None:
    report = build_gpu_provenance()
    print(
        "wrote gpu-provenance/gpu-provenance-report.json and "
        "gpu-provenance/reports/gpu-provenance-report.md "
        f"({report['status']}, {report['measured_run_count']} measured GPU runs)"
    )


if __name__ == "__main__":
    main()
