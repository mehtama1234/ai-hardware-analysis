#!/usr/bin/env python3
"""Build the speculative decoding serving report."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "speculative-decoding-serving"))

from speculative_decoding_serving import build_speculative_decoding_report  # noqa: E402


def main() -> int:
    report = build_speculative_decoding_report()
    print(
        "wrote speculative-decoding-serving/speculative-decoding-report.json and "
        "speculative-decoding-serving/reports/speculative-decoding-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
