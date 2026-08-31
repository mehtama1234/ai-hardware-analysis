#!/usr/bin/env python3
"""Build compiler/runtime inspection report for GPU-facing source files."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "compiler-runtime-inspection"))

from compiler_runtime_inspection import build_compiler_runtime_report  # noqa: E402


def main() -> int:
    report = build_compiler_runtime_report()
    print(
        "wrote compiler-runtime-inspection/compiler-runtime-report.json and "
        "compiler-runtime-inspection/reports/compiler-runtime-report.md "
        f"({report['source_count']} sources, {report['group_count']} groups, status={report['status']})"
    )
    return 0 if report["status"] == "inspection-ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
