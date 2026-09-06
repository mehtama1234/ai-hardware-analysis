#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells"
SOURCE = CELLS / "sky130_latch_precharge_wide_input_flat.mag"
OUT = CELLS / "sky130_latch_precharge_wide_input_medium_feedback_flat.mag"

def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    for old, new in {
        "rect 1560 200 1620 1200": "rect 1550 200 1630 1200",
        "rect 3560 200 3620 1200": "rect 3550 200 3630 1200",
        "rlabel polysilicon 1560 300 1620 1200": "rlabel polysilicon 1550 300 1630 1200",
        "rlabel polysilicon 3560 300 3620 1200": "rlabel polysilicon 3550 300 3630 1200",
    }.items():
        if old not in text:
            raise RuntimeError(old)
        text = text.replace(old, new)
    OUT.write_text(text, encoding="utf-8")
    print(f"created,{OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
