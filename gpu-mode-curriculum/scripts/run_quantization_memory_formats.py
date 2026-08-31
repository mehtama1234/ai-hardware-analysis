#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "quantization-memory-formats"))

from quantization_memory_formats import build_quantization_report


def main() -> int:
    report = build_quantization_report()
    print(
        "wrote quantization-memory-formats/quantization-report.json and "
        "quantization-memory-formats/reports/quantization-report.md "
        f"({report['format_count']} formats, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
