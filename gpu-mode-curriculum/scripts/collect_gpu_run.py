#!/usr/bin/env python3
"""Collect a GPU-host run JSON for import into gpu-runs/."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gpu-runs"))

from gpu_runs.collector import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
