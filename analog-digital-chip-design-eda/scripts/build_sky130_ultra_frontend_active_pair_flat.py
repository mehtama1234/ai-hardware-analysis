#!/usr/bin/env python3
"""Build a flat, routed copy of the frontend-to-active handoff cell."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CELL_DIR = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench" / "cells"
FRONTEND = CELL_DIR / "sky130_ultra_sense_capacitive_frontend.mag"
ACTIVE = CELL_DIR / "sky130_transistor_active_isolation_pair.mag"
OUT = CELL_DIR / "sky130_ultra_frontend_active_pair_flat.mag"


def parse(path: Path, dx: int = 0, dy: int = 0) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = defaultdict(list)
    current = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("<< ") and line.endswith(" >>"):
            current = line[3:-3]
            continue
        if not current or current == "end":
            continue
        if line.startswith("rect "):
            values = line.split()
            values[1:5] = [str(int(values[i]) + (dx if i in (1, 3) else 0) + (dy if i in (2, 4) else 0)) for i in range(1, 5)]
            line = " ".join(values)
        elif current == "labels" and line.startswith("rlabel "):
            values = line.split()
            values[2:6] = [str(int(values[i]) + (dx if i in (2, 4) else 0) + (dy if i in (3, 5) else 0)) for i in range(2, 6)]
            line = " ".join(values)
        sections[current].append(line)
    return sections


def main() -> int:
    merged: dict[str, list[str]] = defaultdict(list)
    for source, dx, dy in ((FRONTEND, 0, 0), (ACTIVE, 4000, 200)):
        for section, lines in parse(source, dx, dy).items():
            if source == ACTIVE and section == "labels":
                # Keep the transistor geometry and route it to the frontend,
                # but replace the child's duplicate port numbers with unique
                # parent-level names below.
                continue
            merged[section].extend(lines)

    # Sense-P: frontend metal2 -> via1 -> metal1 -> polycontact -> active gate.
    merged["metal2"].extend([
        "rect 300 1400 360 1440",
        "rect 3200 1360 3280 1720",
        "rect 3200 1720 4570 1800",
    ])
    merged["metal1"].extend([
        "rect 300 1400 360 1440",
        "rect 300 1360 3240 1440",
        "rect 4570 1720 4610 1800",
    ])
    merged["via1"].extend([
        "rect 300 1400 360 1440",
        "rect 3200 1360 3280 1440",
        "rect 4570 1720 4610 1800",
    ])
    merged["locali"].extend([
        "rect 4570 1720 4610 1800",
    ])
    merged["mcon"].extend([
        "rect 4570 1720 4610 1800",
    ])
    merged["pc"].extend(["rect 4570 1720 4610 1800"])
    merged["polysilicon"].extend(["rect 4560 900 4620 1800"])

    # Sense-N: route above the first gate so it reaches only the second gate.
    merged["metal2"].extend([
        "rect 2840 1400 2880 1960",
        "rect 2840 1920 5780 2000",
        "rect 5780 1920 5860 2000",
    ])
    merged["metal1"].extend(["rect 5780 1920 5840 2000"])
    merged["via1"].extend(["rect 5780 1920 5840 2000"])
    merged["locali"].extend(["rect 5780 1920 5840 2000"])
    merged["mcon"].extend(["rect 5780 1920 5840 2000"])
    merged["pc"].extend(["rect 5780 1920 5840 2000"])
    merged["polysilicon"].extend(["rect 5780 900 5840 1960"])
    merged["labels"].extend([
        "rlabel metal1 4300 820 4500 1000 0 iso_tail_flat",
        "port 10 nsew",
        "rlabel metal1 4700 820 4900 1000 0 iso_p_flat",
        "port 11 nsew",
        "rlabel metal1 5500 820 5700 1000 0 iso_n_flat",
        "port 12 nsew",
    ])

    order = ["ndiffusion", "polysilicon", "ndc", "mcon", "locali", "metal1", "metal2", "via1", "pc", "labels"]
    lines = ["magic", "tech sky130A", "timestamp 1788105600"]
    for section in order:
        if section in merged:
            lines.append(f"<< {section} >>")
            lines.extend(merged[section])
    lines.append("<< end >>")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"created,{OUT}")
    print(f"sections,{len(merged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
