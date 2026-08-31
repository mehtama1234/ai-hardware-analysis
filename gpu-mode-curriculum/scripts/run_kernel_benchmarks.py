#!/usr/bin/env python3
"""Run GPUMODE kernel benchmark families."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kernel-benchmarks"))

from kernel_benchmarks.harness import REPORT_JSON, REPORT_MD, run_all  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run_all(repeats=max(1, args.repeats))
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"wrote {REPORT_JSON.relative_to(ROOT)} and {REPORT_MD.relative_to(ROOT)} ({report['passed']}/{report['benchmark_count']} passed)")
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
