#!/usr/bin/env python3
"""Build the portable GPU-host handoff bundle."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gpu-handoff"))

from gpu_handoff import build_handoff  # noqa: E402


def main() -> None:
    handoff = build_handoff()
    print(
        "wrote gpu-handoff/gpu-host-handoff.json, gpu-handoff/reports/gpu-host-handoff.md, "
        f"and gpu-handoff/bin/run-gpu-host-handoff.sh (status={handoff['status']})"
    )


if __name__ == "__main__":
    main()
