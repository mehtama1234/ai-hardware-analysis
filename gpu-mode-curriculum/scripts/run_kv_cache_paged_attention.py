#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kv-cache-paged-attention"))

from kv_cache_paged_attention import build_kv_cache_report


def main() -> int:
    report = build_kv_cache_report()
    print(
        "wrote kv-cache-paged-attention/kv-cache-report.json and "
        "kv-cache-paged-attention/reports/kv-cache-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
