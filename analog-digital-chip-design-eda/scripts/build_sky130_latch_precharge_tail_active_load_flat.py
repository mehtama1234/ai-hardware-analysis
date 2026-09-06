#!/usr/bin/env python3
"""Assemble the clocked latch parent with the extracted active-load pair."""

from collections import defaultdict
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CELLS = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells"
BASE = CELLS / os.environ.get("AIMC_ACTIVE_LOAD_BASE_CELL", "sky130_latch_precharge_tail_flat.mag")
LOAD = CELLS / "sky130_cross_coupled_pmos_load_pair_starter.mag"
OUT = CELLS / os.environ.get("AIMC_ACTIVE_LOAD_OUT_CELL", "sky130_latch_precharge_tail_active_load_flat.mag")


def parse(path: Path, dx=0, dy=0, stretch_right=False):
    result = defaultdict(list)
    section = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("<< ") and raw.endswith(" >>"):
            section = raw[3:-3]
            continue
        if not section or section == "end":
            continue
        if raw.startswith("rect "):
            p = raw.split()
            xs = [int(p[1]), int(p[3])]
            if stretch_right:
                xs = [x + (1000 if x >= 1100 else 0) for x in xs]
            p[1], p[2], p[3], p[4] = str(xs[0] + dx), str(int(p[2]) + dy), str(xs[1] + dx), str(int(p[4]) + dy)
            raw = " ".join(p)
        elif section == "labels" and raw.startswith("rlabel "):
            p = raw.split()
            label_x = [int(p[2]), int(p[4])]
            if stretch_right:
                label_x = [x + (1000 if x >= 1100 else 0) for x in label_x]
            p[2], p[4] = str(label_x[0] + dx), str(label_x[1] + dx)
            p[3], p[5] = str(int(p[3]) + dy), str(int(p[5]) + dy)
            raw = " ".join(p)
        result[section].append(raw)
    return result


def main() -> int:
    subprocess.run(["python3", str(ROOT / "scripts/build_sky130_cross_coupled_pmos_load_pair.py")], cwd=ROOT, check=True)
    merged = parse(BASE)
    # Place the active load above the existing parent.  Keeping it in the
    # same x-window makes the output handoff short and leaves the tail block
    # and its evaluation routing untouched.
    for section, lines in parse(LOAD, 0, 4000, stretch_right=True).items():
        if section != "labels":
            merged[section].extend(lines)

    # The stretched active-load outputs align with the parent latch outputs.
    # Use the existing metal2 trunks for a vertical, non-crossing handoff.
    merged["metal3"] += ["rect 800 2600 860 4760", "rect 2800 2860 2860 4760"]
    merged["via2"] += ["rect 800 2540 860 2600", "rect 2800 2740 2860 2800", "rect 800 4700 860 4760", "rect 2800 4700 2860 4760"]
    # Preserve the active-load supply identity after flattening.  Its output
    # labels are intentionally inherited from the parent handoff; only VDD
    # needs an explicit local label because the load was added without ports.
    merged["labels"] += [
        "rlabel metal1 400 4620 600 4800 0 vdd_active",
        "rlabel metal1 2400 4620 2600 4800 0 vdd_active",
        "rlabel metal1 3100 4600 3160 4700 0 vdd_active",
    ]

    order = ["nwell", "pdiffusion", "ndiffusion", "nsubdiff", "nsubdiffcont", "polysilicon", "pdc", "ndc", "pc", "locali", "mcon", "viali", "metal1", "metal2", "metal3", "metal4", "via1", "via2", "via3", "labels"]
    lines = ["magic", "tech sky130A", "timestamp 1788105600"]
    for section in order:
        if section in merged:
            lines += [f"<< {section} >>", *merged[section]]
    lines.append("<< end >>")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"created,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
