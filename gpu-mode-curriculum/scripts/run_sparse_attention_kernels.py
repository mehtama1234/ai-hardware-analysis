#!/usr/bin/env python3
"""Build the sparse attention kernel report."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sparse-attention-kernels"))

from sparse_attention_kernels import build_sparse_attention_report


def main() -> None:
    report = build_sparse_attention_report()
    print(
        "wrote sparse-attention-kernels/sparse-attention-report.json and "
        "sparse-attention-kernels/reports/sparse-attention-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )


if __name__ == "__main__":
    main()
