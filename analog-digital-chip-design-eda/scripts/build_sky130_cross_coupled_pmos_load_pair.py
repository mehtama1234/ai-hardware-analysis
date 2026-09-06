#!/usr/bin/env python3
"""Build a matched cross-coupled PMOS active-load starter from the verified pair."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench" / "cells"
SOURCE = CELLS / "sky130_pmos_precharge_pair_starter.mag"
TARGET = CELLS / "sky130_cross_coupled_pmos_load_pair_starter.mag"


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    text = text.replace("sky130_pmos_precharge_pair_starter", "sky130_cross_coupled_pmos_load_pair_starter")
    text = text.replace("precharge_p", "out_p").replace("precharge_n", "out_n")
    # The two PMOS gates are no longer reset gates: each gate is driven by
    # the opposite regenerative output.  The labels are on polysilicon so
    # Magic preserves the gate-to-device connectivity in extraction.
    text = text.replace("rlabel polysilicon 660 200 720 1200 0 reset\nport 5 nsew\n", "")
    text = text.replace("rlabel polysilicon 1660 200 1720 1200 0 reset\nport 6 nsew\n", "")
    text = text.replace("rlabel metal1 400 620 600 800 0 vdd", "rlabel metal1 400 620 600 800 0 vdd")
    text = text.replace("rlabel metal1 1400 620 1600 800 0 vdd", "rlabel metal1 1400 620 1600 800 0 vdd")
    text = text.replace("<< polysilicon >>", """<< nsubdiff >>
rect 2100 600 2160 700
<< nsubdiffcont >>
rect 2100 600 2160 700
<< locali >>
rect 2100 600 2160 700
<< viali >>
rect 2100 600 2160 700
<< metal1 >>
rect 2100 600 2160 700
<< polysilicon >>""")
    # Explicit feedback routes: out_n (left diffusion) drives the right
    # PMOS gate on metal2; out_p (right diffusion) drives the left gate on
    # metal3 so the two crossing signals remain separated.
    text = text.replace("timestamp 1788105000\n", """timestamp 1788105000
""")
    text = text.replace("<< labels >>", """<< metal2 >>
rect 800 700 860 760
rect 800 700 1720 760
rect 1660 250 1720 760
rect 1800 700 1860 760
<< metal2 >>
rect 440 780 500 1000
rect 1440 780 1500 1000
rect 440 940 2100 1000
rect 2070 600 2130 1000
<< via1 >>
rect 800 700 860 760
rect 1800 700 1860 760
rect 440 780 500 840
rect 1440 780 1500 840
rect 2070 600 2130 660
<< via2 >>
rect 660 250 720 300
rect 1800 700 1860 760
<< metal3 >>
rect 660 900 1860 960
rect 660 250 720 960
rect 1800 700 1860 960
<< labels >>""")
    TARGET.write_text(text, encoding="utf-8")
    print(TARGET)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
