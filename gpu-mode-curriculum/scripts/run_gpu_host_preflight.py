#!/usr/bin/env python3
"""Run GPU-host handoff preflight checks."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gpu-handoff"))
sys.path.insert(0, str(ROOT / "gpu-promotion"))

from gpu_handoff.preflight import build_preflight  # noqa: E402


def main() -> None:
    report = build_preflight()
    print(
        "wrote gpu-handoff/gpu-host-preflight.json and gpu-handoff/reports/gpu-host-preflight.md "
        f"({report['status']}, {report['runnable_step_count']}/{report['step_count']} runnable)"
    )


if __name__ == "__main__":
    main()
