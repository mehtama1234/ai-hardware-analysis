#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "flash-attention-backward"))

from flash_attention_backward import build_flash_attention_backward_report


def main() -> int:
    report = build_flash_attention_backward_report()
    print(
        "wrote flash-attention-backward/flash-attention-backward-report.json and "
        "flash-attention-backward/reports/flash-attention-backward-report.md "
        f"({report['scenario_count']} scenarios, status={report['status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
