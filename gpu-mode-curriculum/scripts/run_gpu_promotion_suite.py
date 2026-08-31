#!/usr/bin/env python3
"""Plan or execute the GPU promotion suite from the generated manifest."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gpu-promotion"))

from gpu_promotion.suite_runner import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
