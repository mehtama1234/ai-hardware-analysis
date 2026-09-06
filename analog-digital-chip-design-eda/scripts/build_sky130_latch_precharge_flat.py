#!/usr/bin/env python3
"""Flatten the extracted latch starter and PMOS precharge pair into one parent."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench" / "cells"
LATCH = CELLS / "sky130_regenerative_latch_starter.mag"
PRE = CELLS / "sky130_pmos_precharge_pair_starter.mag"
OUT = CELLS / "sky130_latch_precharge_flat.mag"


def parse(path: Path, dx: int = 0) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = defaultdict(list)
    current = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("<< ") and raw.endswith(" >>"):
            current = raw[3:-3]
            continue
        if not current or current == "end":
            continue
        if raw.startswith("rect "):
            parts = raw.split()
            parts[1] = str(int(parts[1]) + dx)
            parts[3] = str(int(parts[3]) + dx)
            raw = " ".join(parts)
        elif current == "labels" and raw.startswith("rlabel "):
            parts = raw.split()
            parts[2] = str(int(parts[2]) + dx)
            parts[4] = str(int(parts[4]) + dx)
            raw = " ".join(parts)
        sections[current].append(raw)
    return sections


def main() -> int:
    merged: dict[str, list[str]] = defaultdict(list)
    for source, dx in ((LATCH, 0), (PRE, 6000)):
        for section, lines in parse(source, dx).items():
            if source == PRE and section == "labels":
                continue
            merged[section].extend(lines)

    # PMOS-P source -> VDD: metal1/via1/metal2/via2/metal3 bridge.
    merged["metal2"] += ["rect 6460 620 6520 1000", "rect 7460 620 7520 1000"]
    merged["via1"] += ["rect 6460 620 6520 680", "rect 7460 620 7520 680"]
    merged["via2"] += ["rect 6460 950 6520 1010", "rect 7460 950 7520 1010"]
    merged["metal3"] += ["rect 6460 950 7520 1010"]

    # PMOS drains to latch outputs. P uses metal3; N uses metal4 to avoid a crossing.
    merged["metal2"] += ["rect 6800 780 6860 2600", "rect 800 780 860 2600", "rect 7800 780 7860 2800", "rect 2800 780 2860 2800"]
    merged["via1"] += ["rect 6800 780 6860 840", "rect 800 780 860 840", "rect 7800 780 7860 840", "rect 2800 780 2860 840"]
    merged["via2"] += ["rect 6800 2540 6860 2600", "rect 800 2540 860 2600", "rect 7800 2740 7860 2800", "rect 2800 2740 2860 2800"]
    merged["metal3"] += ["rect 800 2540 860 2600", "rect 800 2540 6800 2600", "rect 6800 2540 6860 2600", "rect 2800 2740 2860 2860"]
    merged["via3"] += ["rect 2800 2740 2860 2800", "rect 7800 2740 7860 2800"]
    merged["metal4"] += ["rect 2800 2740 2860 2860", "rect 2800 2740 7800 2800", "rect 7800 2740 7860 2860"]

    # Join the two PMOS reset gates on metal3.
    merged["metal3"] += ["rect 6660 250 7720 300"]
    merged["via2"] += ["rect 6660 250 6720 300", "rect 7660 250 7720 300"]
    merged["labels"] += ["rlabel metal3 7000 250 7400 300 0 reset", "port 20 nsew", "rlabel metal3 6900 950 7200 1010 0 vdd", "port 21 nsew"]

    order = ["nwell", "pdiffusion", "ndiffusion", "polysilicon", "pdc", "ndc", "pc", "locali", "mcon", "metal1", "metal2", "metal3", "metal4", "via1", "via2", "via3", "labels"]
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
