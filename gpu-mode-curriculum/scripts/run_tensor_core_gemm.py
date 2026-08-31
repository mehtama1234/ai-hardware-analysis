#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tensor-core-gemm"))

from tensor_core_gemm import build_tensor_core_gemm_report


def main() -> int:
    report = build_tensor_core_gemm_report()
    print(
        "wrote tensor-core-gemm/tensor-core-gemm-report.json and "
        "tensor-core-gemm/reports/tensor-core-gemm-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
