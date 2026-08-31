#!/usr/bin/env python3
"""Parse profiler-shaped fixtures and emit a normalized evidence report."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "profiler-evidence"))

from profiler_evidence.parser import REPORT_JSON, REPORT_MD, build_report  # noqa: E402


def main() -> int:
    report = build_report()
    print(f"wrote {REPORT_JSON.relative_to(ROOT)} and {REPORT_MD.relative_to(ROOT)} ({report['row_count']} rows)")
    return 0 if all(report["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
