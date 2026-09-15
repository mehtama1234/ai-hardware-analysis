#!/usr/bin/env python3
"""Generate one explicit SKY130 NFET preamp cell for parent integration."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--name", default="preamp_nfet")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    name = args.name
    mag = f'''magic
tech sky130A
timestamp 1789000000
<< ndiffusion >>
rect 300 690 900 810
<< polysilicon >>
rect 560 200 620 1200
<< ndc >>
rect 340 700 460 760
rect 740 700 860 760
<< mcon >>
rect 560 250 620 300
rect 340 700 460 760
rect 740 700 860 760
<< metal1 >>
rect 540 250 640 300
rect 300 620 500 800
rect 700 620 900 800
rect 1000 1800 1200 1900
<< metal2 >>
rect 500 250 680 300
<< via1 >>
rect 500 250 680 300
<< pc >>
rect 560 250 620 300
<< locali >>
rect 560 250 620 300
<< psubdiff >>
rect 1000 1800 1200 1900
<< psubdiffcont >>
rect 1000 1800 1200 1900
<< viali >>
rect 1000 1800 1200 1900
<< labels >>
rlabel metal1 300 620 500 800 0 source
port 1 nsew
rlabel metal1 700 620 900 800 0 drain
port 2 nsew
rlabel metal2 500 250 680 300 0 gate
port 3 nsew
rlabel metal1 1000 1800 1200 1900 0 body
port 4 nsew
<< end >>
'''
    (out / f"{name}.mag").write_text(mag, encoding="utf-8")
    (out / "reference.spice").write_text(
        f".subckt {name} source drain gate body\n"
        "X0 drain gate source body sky130_fd_pr__nfet_01v8 w=1.2 l=0.6\n"
        f".ends {name}\n", encoding="utf-8")
    (out / "extract.tcl").write_text(
        f"load {name} -force\nselect top cell\ndrc check\ndrc count\n"
        "extract all\next2spice lvs\next2spice cthresh 0\next2spice rthresh 0\n"
        "ext2spice -o extracted.spice\nquit -noprompt\n", encoding="utf-8")
    (out / "build.json").write_text(json.dumps({
        "result_type": "single_preamp_cell",
        "cell": name,
        "ports": ["source", "drain", "gate", "body"],
        "accepted_converter": False,
        "claim_boundary": "One-device cell only; requires extraction/LVS before parent integration."
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
