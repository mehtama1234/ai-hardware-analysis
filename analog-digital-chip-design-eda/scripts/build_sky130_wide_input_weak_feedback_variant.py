#!/usr/bin/env python3
"""Create a widened-sense, lengthened-feedback latch/precharge variant."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench" / "cells"
SOURCE = CELLS / "sky130_latch_precharge_wide_input_flat.mag"
OUT = CELLS / "sky130_latch_precharge_wide_input_weak_feedback_flat.mag"


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    for old, new in {
        "rect 1560 200 1620 1200": "rect 1530 200 1650 1200",
        "rect 3560 200 3620 1200": "rect 3530 200 3650 1200",
        "rlabel polysilicon 1560 300 1620 1200": "rlabel polysilicon 1530 300 1650 1200",
        "rlabel polysilicon 3560 300 3620 1200": "rlabel polysilicon 3530 300 3650 1200",
    }.items():
        if old not in text:
            raise RuntimeError(f"missing expected source text: {old}")
        text = text.replace(old, new)
    OUT.write_text(text, encoding="utf-8")
    print(f"created,{OUT}")
    print("feedback_gate_length_variant,2x_nominal_poly_width")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
