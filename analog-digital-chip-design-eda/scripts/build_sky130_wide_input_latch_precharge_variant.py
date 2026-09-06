#!/usr/bin/env python3
"""Create a variant with a wider matched sense pair for physical comparison."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench" / "cells"
SOURCE = CELLS / "sky130_latch_precharge_flat.mag"
OUT = CELLS / "sky130_latch_precharge_wide_input_flat.mag"


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    replacements = {
        "rect 300 690 900 810": "rect 300 400 900 1000",
        "rect 2300 690 2900 810": "rect 2300 400 2900 1000",
    }
    for old, new in replacements.items():
        if text.count(old) != 1:
            raise RuntimeError(f"expected one source geometry: {old}")
        text = text.replace(old, new)
    text = text.replace("sky130_latch_precharge_flat", "sky130_latch_precharge_wide_input_flat")
    OUT.write_text(text, encoding="utf-8")
    print(f"created,{OUT}")
    print("sense_pair_width_variant,5x_nominal_diffusion_height_target")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
