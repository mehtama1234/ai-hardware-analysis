#!/usr/bin/env python3
"""Top-level entry point for checkpoint resume validation."""

from __future__ import annotations

import runpy
from pathlib import Path


TARGET = (
    Path(__file__).resolve().parents[1]
    / "analog-digital-chip-design-eda"
    / "scripts"
    / "resume_four_workstream_pipeline.py"
)


if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
