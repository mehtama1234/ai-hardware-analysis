#!/usr/bin/env python3
"""Top-level entry point for structural IR validation."""
from __future__ import annotations
import runpy
from pathlib import Path
TARGET = Path(__file__).resolve().parents[1] / "analog-digital-chip-design-eda" / "scripts" / "check_real_multimodule_structural_ir.py"
if __name__ == "__main__": runpy.run_path(str(TARGET), run_name="__main__")
