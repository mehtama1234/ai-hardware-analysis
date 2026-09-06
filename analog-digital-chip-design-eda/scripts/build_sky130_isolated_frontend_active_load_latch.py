#!/usr/bin/env python3
"""Compose the verified transistor isolation pair ahead of the active-load latch."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells"
BASE = CELLS / "sky130_latch_precharge_tail_active_load_flat.mag"
ISOLATOR = CELLS / "sky130_transistor_active_isolation_pair.mag"
OUT = CELLS / "sky130_isolated_frontend_active_load_latch_v2.mag"


def parse(path: Path, dx: int = 0, dy: int = 0, rename_latch_inputs: bool = False):
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
            p[1] = str(int(p[1]) + dx)
            p[2] = str(int(p[2]) + dy)
            p[3] = str(int(p[3]) + dx)
            p[4] = str(int(p[4]) + dy)
            raw = " ".join(p)
        elif section == "labels" and raw.startswith("rlabel "):
            p = raw.split()
            if rename_latch_inputs and p[-1] in {"sense_p", "sense_n"}:
                p[-1] = "latch_sense_p" if p[-1] == "sense_p" else "latch_sense_n"
            p[2] = str(int(p[2]) + dx)
            p[3] = str(int(p[3]) + dy)
            p[4] = str(int(p[4]) + dx)
            p[5] = str(int(p[5]) + dy)
            raw = " ".join(p)
        result[section].append(raw)
    return result


def main() -> int:
    merged = parse(BASE, rename_latch_inputs=True)
    # Place the isolator below the existing latch.  Its outputs are routed to
    # the latch gates; its sense gates remain top-level inputs.
    for section, lines in parse(ISOLATOR, dy=6000).items():
        if section != "labels":
            # This unused primitive metal2 strip becomes a P/N short when
            # the new output vias land on it. Neither output needs it.
            merged[section].extend(line for line in lines if not
                                   (section == "metal2" and line == "rect 450 6700 1950 6760"))

    # The input gates are x=560 and x=2560. x=3560 is feedback/out_n.
    # Metal4 routes avoid the base cell's metal3 output and tail trunks.
    for x in (560, 2560):
        merged["pc"].append(f"rect {x} 250 {x + 60} 300")
        merged["mcon"].append(f"rect {x} 250 {x + 60} 300")
        merged["metal1"].append(f"rect {x} 250 {x + 60} 300")
        merged["via1"].append(f"rect {x} 250 {x + 60} 300")
        merged["metal2"].append(f"rect {x} 250 {x + 60} 300")
        merged["via2"].append(f"rect {x} 250 {x + 60} 300")
        merged["metal3"].append(f"rect {x} 250 {x + 60} 300")
        merged["via3"].append(f"rect {x} 250 {x + 60} 300")
        merged["metal4"].append(f"rect {x} 250 {x + 60} 300")

    # Isolator iso_p (x=700..900) drives latch sense_p gate (x=560..620).
    merged["via1"] += ["rect 780 6660 840 6720", "rect 1580 6660 1640 6720"]
    merged["via2"] += ["rect 780 6660 840 6720", "rect 1580 6660 1640 6720"]
    merged["metal2"] += ["rect 780 6660 840 6720", "rect 1580 6660 1640 6720"]
    merged["metal3"] += [
        "rect 780 6660 840 6720",
        "rect 1580 6660 1640 6720",
    ]
    merged["via3"] += ["rect 780 6660 840 6720", "rect 1580 6660 1640 6720"]
    merged["metal4"] += [
        "rect 560 6660 840 6720",
        "rect 560 250 620 6720",
        "rect 1580 6660 2620 6720",
        # Detour outside existing metal4 feedback at y=1400..1460.
        "rect 2560 1500 2620 6720",
        "rect 2560 1500 4160 1560",
        "rect 4100 100 4160 1560",
        "rect 2560 100 4160 160",
        "rect 2560 100 2620 300",
    ]

    merged["labels"] += [
        "rlabel polysilicon 560 6300 620 7200 0 sense_p",
        "port 40 nsew",
        "rlabel polysilicon 1780 6300 1840 7200 0 sense_n",
        "port 41 nsew",
        "rlabel metal1 300 6620 500 6800 0 iso_tail",
        "port 42 nsew",
        "rlabel metal1 400 4620 600 4800 0 vdd_active",
        "port 43 nsew",
    ]

    # Physically tie the common NFET substrate to VSS and the precharge
    # PMOS well to VDD. The base active-load well already has its own tie.
    for layer in ("psubdiff", "psubdiffcont", "locali", "viali", "metal1"):
        merged[layer].append("rect 4500 3400 4560 3500")
    merged["metal1"] += ["rect 4500 3400 4920 3460", "rect 4860 2500 4920 3460"]
    for layer in ("nsubdiff", "nsubdiffcont", "locali", "viali", "metal1"):
        merged[layer].append("rect 8100 600 8160 700")
    # Metal1 above the diffusion avoids crossing the metal2 output trunk.
    merged["metal1"] += ["rect 8100 600 8160 1380", "rect 7460 1320 8160 1380", "rect 7460 640 7520 1380"]

    order = [
        "nwell", "pdiffusion", "ndiffusion", "nsubdiff", "nsubdiffcont", "psubdiff", "psubdiffcont",
        "polysilicon", "pdc", "ndc", "pc", "locali", "mcon", "viali",
        "metal1", "metal2", "metal3", "metal4", "via1", "via2", "via3",
        "labels",
    ]
    lines = ["magic", "tech sky130A", "timestamp 1788106000"]
    for section in order:
        if section in merged:
            lines += [f"<< {section} >>", *merged[section]]
    lines.append("<< end >>")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"created,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
