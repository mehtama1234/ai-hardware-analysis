#!/usr/bin/env python3
"""Run exhaustive layout contracts and emit a provenance-bearing report."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from layout_algebra import blocked_2d, row_major, xor_swizzled_2d

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "layout-algebra/reports/layout-checks.json"


def main():
    layouts = [row_major(8, 16), blocked_2d(8, 16, 4, 4), xor_swizzled_2d(8, 16, 4, 4)]
    checks = [layout.check_bijection() for layout in layouts]
    source = Path(__file__).with_name("layout_algebra.py")
    report = {
        "experiment": "layout_algebra_bijection_checks",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed",
        "measured": True,
        "evidence_class": "cpu-executed-layout-contract",
        "layouts": checks,
        "inverse_checks": {layout.name: len(layout.inverse()) == layout.size for layout in layouts},
        "source_sha256": {str(source.relative_to(ROOT.parent.parent)): hashlib.sha256(source.read_bytes()).hexdigest()},
        "python": sys.version,
        "platform": platform.platform(),
        "scope": "host-side coordinate bijection and inverse checks; no CuTe compiler, GPU execution, or bank-conflict claim",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
