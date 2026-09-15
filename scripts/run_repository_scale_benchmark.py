#!/usr/bin/env python3
"""Top-level entry point for the repository-scale benchmark CLI.

The implementation belongs to the digital-EDA subproject, but repository
automation and users invoke benchmark commands from the monorepo root.
Forwarding through ``runpy`` preserves the implementation's own module path
and keeps the two entry points behaviorally identical.
"""

from __future__ import annotations

import runpy
from pathlib import Path


TARGET = (
    Path(__file__).resolve().parents[1]
    / "analog-digital-chip-design-eda"
    / "scripts"
    / "run_repository_scale_benchmark.py"
)


if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
