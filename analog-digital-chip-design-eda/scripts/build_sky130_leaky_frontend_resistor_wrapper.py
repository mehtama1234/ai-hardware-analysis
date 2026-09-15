#!/usr/bin/env python3
"""Add drawn Sky130 high-resistance poly leakage paths around the derived frontend."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench"
CELLS = WORKBENCH / "cells"
EXTRACTED = WORKBENCH / "extracted"
SOURCE = CELLS / "sky130_leaky_ultra_sense_capacitive_frontend.mag"
CELL = "sky130_leaky_frontend_resistor_wrapper"
MAG = CELLS / f"{CELL}.mag"
SPICE = EXTRACTED / f"{CELL}_extracted.spice"
OUT = ROOT / "evidence/aimc-simulator-adapters/sky130-leaky-frontend-resistor-wrapper-physical.json"
MAGIC = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools/magic-8.3.682/bin/magic")))
PDK = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools/pdks")))
MAGIC_RC = PDK / "sky130A/libs.tech/magic/sky130A.magicrc"

REGIONS = (
    "ultra_sample_p_sense_p_region",
    "ultra_sample_n_sense_n_region",
    "symmetric_reset_region",
    "symmetric_latch_clock_region",
)
# Interior points of the four derived frontend regions, followed by dedicated
# metal3 via landings kept clear of the original metal2 signal buses.
REGION_POINTS = ((440, 800), (2760, 800), (1600, 1080), (1600, 520))
# Descending x positions prevent a lower branch's vertical drop from crossing
# a higher branch's horizontal run on the same metal layer.
TAP_POINTS = ((2100, 800), (1700, 800), (1300, 1080), (1100, 520))
RESISTOR_YS = (3000, 5000, 7000, 9000)
RESISTOR_X1 = 5000
RESISTOR_X2 = 11900
COMMON_X = 13000


def parse(source: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = defaultdict(list)
    section = ""
    for line in source.splitlines():
        if line.startswith("<< ") and line.endswith(" >>"):
            section = line[3:-3]
        elif section and section != "end":
            sections[section].append(line)
    return sections


def build_geometry() -> str:
    sections = parse(SOURCE.read_text(encoding="utf-8"))
    # The derived child ports become internal labels in this flat wrapper.
    filtered: list[str] = []
    for line in sections["labels"]:
        if line.startswith("port ") and line.split()[1] in {"10", "11", "12", "13"}:
            continue
        filtered.append(line)
    sections["labels"] = filtered

    def rect(layer: str, x1: int, y1: int, x2: int, y2: int) -> None:
        sections[layer].append(f"rect {min(x1, x2)} {min(y1, y2)} {max(x1, x2)} {max(y1, y2)}")

    def wire(layer: str, x1: int, y1: int, x2: int, y2: int) -> None:
        if x1 != x2 and y1 != y2:
            raise ValueError("only Manhattan routes are supported")
        rect(layer, x1 - 30, y1 - 30, x2 + 30, y2 + 30)

    def via(x: int, y: int, lo: int = 1, hi: int = 3) -> None:
        for level in range(lo, hi + 1):
            rect(f"metal{level}", x - 40, y - 40, x + 40, y + 40)
            if level < hi:
                rect(f"via{level}", x - 30, y - 30, x + 30, y + 30)

    # Each uhrpoly strip is 0.69 um wide and 34.5 um long: approximately
    # 50 squares at the PDK's 2 kOhm/square nominal sheet resistance.
    for index, (name, (src_x, src_y), (tap_x, tap_y), resistor_y) in enumerate(zip(REGIONS, REGION_POINTS, TAP_POINTS, RESISTOR_YS), start=1):
        rect("uhrpoly", RESISTOR_X1, resistor_y - 69, RESISTOR_X2, resistor_y + 69)
        for x in (RESISTOR_X1, RESISTOR_X2):
            rect("xpc", x - 200, resistor_y - 200, x + 200, resistor_y + 200)
            rect("li", x - 200, resistor_y - 200, x + 200, resistor_y + 200)
            # Sky130's resistor contact lands on local interconnect; bridge
            # that landing to metal1 before climbing to the metal3 route.
            rect("mcon", x - 40, resistor_y - 40, x + 40, resistor_y + 40)
            via(x, resistor_y)
        # Reach each named metal1 region first, then climb to metal3 at a
        # dedicated landing clear of the frontend's metal2 signal buses.
        wire("metal1", src_x, src_y, tap_x, tap_y)
        via(tap_x, tap_y, 1, 3)
        sections["labels"].append(f"rlabel metal3 {tap_x - 40} {tap_y - 40} {tap_x + 40} {tap_y + 40} 0 {name}")
        wire("metal3", RESISTOR_X2, resistor_y, COMMON_X, resistor_y)
        wire("metal3", RESISTOR_X1, resistor_y, tap_x, resistor_y)
        wire("metal3", tap_x, resistor_y, tap_x, tap_y)
        # Label the extracted resistor-side landing as a diagnostic anchor;
        # extraction will collapse it onto the region name when the route is
        # electrically continuous.
        sections["labels"].append(f"rlabel metal1 {RESISTOR_X1 - 40} {resistor_y - 40} {RESISTOR_X1 + 40} {resistor_y + 40} 0 {name}")
        via(RESISTOR_X1, resistor_y, 1, 3)
        via(RESISTOR_X2, resistor_y, 1, 3)
    via(COMMON_X, 6000, 1, 3)
    wire("metal3", COMMON_X, 3000, COMMON_X, 9000)
    sections["labels"] += ["rlabel metal3 12940 5960 13060 6040 0 float_cm", "port 14 nsew"]

    order = ["nwell", "pdiffusion", "ndiffusion", "nsubdiff", "nsubdiffcont", "psubdiff", "psubdiffcont",
             "polysilicon", "uhrpoly", "xpc", "li", "pc", "locali", "mcon", "viali", "metal1", "metal2",
             "metal3", "metal4", "via1", "via2", "via3", "labels"]
    lines = ["magic", "tech sky130A", "timestamp 1788729000"]
    for section in order:
        if sections.get(section):
            lines += [f"<< {section} >>", *sections[section]]
    return "\n".join(lines + ["<< end >>", ""]) 


def main() -> int:
    MAG.write_text(build_geometry(), encoding="utf-8")
    EXTRACTED.mkdir(parents=True, exist_ok=True)
    commands = "\n".join([f"path search +{CELLS}", f"load {CELL} -force", "select top cell", "drc on", "drc catchup", "drc count", "extract all", "ext2spice lvs", "ext2spice cthresh 0", "ext2spice rthresh 0", f"ext2spice -o {SPICE.name}", "quit -noprompt", ""])
    proc = subprocess.run([str(MAGIC), "-dnull", "-noconsole", "-rcfile", str(MAGIC_RC)], cwd=EXTRACTED, input=commands, text=True, capture_output=True, check=False, timeout=120, env={**os.environ, "PDK_ROOT": str(PDK)})
    output = proc.stdout + proc.stderr
    counts = re.findall(r"Total DRC errors found:\s*(\d+)", output, flags=re.IGNORECASE)
    extracted = SPICE.read_text(encoding="utf-8") if SPICE.exists() else ""
    headers = [line for line in extracted.splitlines() if line.startswith(".subckt") or line.startswith("+")][:3]
    resistor_lines = [line for line in extracted.splitlines() if "res_xhigh" in line or line.startswith("R")]
    topology_passed = all(name in "\n".join(resistor_lines) for name in (*REGIONS, "float_cm")) and len(resistor_lines) == 4
    report = {
        "result_type": "sky130_leaky_frontend_resistor_wrapper_physical",
        "status": "leaky_frontend_resistor_wrapper_drc_extract_topology_passed_not_transient_or_lvs" if proc.returncode == 0 and counts and int(counts[-1]) == 0 and topology_passed else "leaky_frontend_resistor_wrapper_physical_check_incomplete",
        "source_layout": str(SOURCE.relative_to(ROOT)), "derived_layout": str(MAG.relative_to(ROOT)), "extracted_netlist": str(SPICE.relative_to(ROOT)),
        "resistor_count": 4, "topology_passed": topology_passed, "nominal_resistor_width_um": 0.69, "nominal_resistor_length_um": 34.5, "nominal_sheet_resistance_ohm": 2000,
        "drc_errors": int(counts[-1]) if counts else None, "magic_returncode": proc.returncode, "extracted_subckt_header": "\n".join(headers), "extracted_resistor_lines": resistor_lines,
        "sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in (("layout.mag", MAG), ("extracted.spice", SPICE)) if path.exists()},
        "accepted_post_layout_written": False,
        "claim_boundary": "Drawn uhrpoly resistor wrapper with extracted endpoint topology only; does not prove extracted resistance, leakage corner behavior, full frontend LVS, transient polarity, or converter acceptance.",
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}"); print(f"drc_errors,{report['drc_errors']}"); print(f"resistor_lines,{len(resistor_lines)}"); print(f"json,{OUT}")
    return 0 if report["status"].startswith("leaky_frontend_resistor_wrapper_drc_extract_topology_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
