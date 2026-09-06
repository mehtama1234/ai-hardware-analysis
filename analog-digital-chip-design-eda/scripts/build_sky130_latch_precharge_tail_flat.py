#!/usr/bin/env python3
from __future__ import annotations
from collections import defaultdict
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells"
BASE = CELLS / os.environ.get("AIMC_LATCH_BASE_CELL", "sky130_latch_precharge_flat.mag")
TAIL = CELLS / "sky130_clocked_tail_switch_starter.mag"
OUT = CELLS / os.environ.get("AIMC_LATCH_TAIL_OUT_CELL", "sky130_latch_precharge_tail_flat.mag")

def parse(path: Path, dx=0, dy=0):
    out=defaultdict(list); section=""
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("<< ") and raw.endswith(" >>"):
            section=raw[3:-3]; continue
        if not section or section == "end": continue
        if raw.startswith("rect "):
            p=raw.split(); p[1]=str(int(p[1])+dx); p[2]=str(int(p[2])+dy); p[3]=str(int(p[3])+dx); p[4]=str(int(p[4])+dy); raw=" ".join(p)
        elif section == "labels" and raw.startswith("rlabel "):
            p=raw.split(); p[2]=str(int(p[2])+dx); p[4]=str(int(p[4])+dx); p[3]=str(int(p[3])+dy); p[5]=str(int(p[5])+dy); raw=" ".join(p)
        out[section].append(raw)
    return out

def main():
    merged=parse(BASE)
    for section, lines in parse(TAIL,4500,1800).items():
        if section != "labels": merged[section].extend(lines)
    merged["metal2"] += ["rect 1200 1120 1260 2420", "rect 5200 2420 5260 2480"]
    merged["via1"] += ["rect 1200 1120 1260 1180", "rect 5200 2420 5260 2480"]
    merged["via2"] += ["rect 1200 2360 1260 2420", "rect 5200 2420 5260 2480"]
    merged["metal3"] += ["rect 1200 2360 1260 2420", "rect 1200 2360 5260 2420"]
    merged["labels"] += ["rlabel metal1 4800 2420 5000 2600 0 vss", "port 30 nsew", "rlabel metal2 5000 2050 5180 2100 0 eval", "port 31 nsew"]
    order=["nwell","pdiffusion","ndiffusion","polysilicon","pdc","ndc","pc","locali","mcon","metal1","metal2","metal3","metal4","via1","via2","via3","labels"]
    lines=["magic","tech sky130A","timestamp 1788105600"]
    for s in order:
        if s in merged: lines += [f"<< {s} >>", *merged[s]]
    lines.append("<< end >>"); OUT.write_text("\n".join(lines)+"\n",encoding="utf-8"); print(f"created,{OUT}")
if __name__=="__main__": main()
