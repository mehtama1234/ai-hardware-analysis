#!/usr/bin/env python3
"""Expose the extracted frontend's floating regions for physical leakage study."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench"
CELLS = WORKBENCH / "cells"
EXTRACTED = WORKBENCH / "extracted"
SOURCE_CELL = CELLS / "sky130_ultra_sense_capacitive_frontend.mag"
CELL = "sky130_leaky_ultra_sense_capacitive_frontend"
MAG = CELLS / f"{CELL}.mag"
OUT_SPICE = EXTRACTED / f"{CELL}_extracted.spice"
OUT = ROOT / "evidence/aimc-simulator-adapters/sky130-leaky-ultra-sense-frontend-physical.json"
MAGIC = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools/magic-8.3.682/bin/magic")))
PDK = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools/pdks")))
MAGIC_RC = PDK / "sky130A/libs.tech/magic/sky130A.magicrc"


REGIONS = (
    "ultra_sample_p_sense_p_region",
    "ultra_sample_n_sense_n_region",
    "symmetric_reset_region",
    "symmetric_latch_clock_region",
)


def build_mag() -> None:
    text = SOURCE_CELL.read_text(encoding="utf-8")
    if "port 9 nsew\n" not in text:
        raise RuntimeError("source frontend port contract changed")
    for index, name in enumerate(REGIONS, start=10):
        marker = f"rlabel metal1 "
        lines = text.splitlines()
        matches = [line for line in lines if line.endswith(f"0 {name}")]
        if len(matches) != 1:
            raise RuntimeError(f"expected one region label: {name}")
        label = matches[0]
        text = text.replace(label + "\n", label + f"\nport {index} nsew\n", 1)
    MAG.write_text(text, encoding="utf-8")


def main() -> int:
    build_mag()
    EXTRACTED.mkdir(parents=True, exist_ok=True)
    commands = "\n".join([
        f"path search +{CELLS}",
        f"load {CELL} -force",
        "select top cell",
        "drc on",
        "drc catchup",
        "drc count",
        "extract all",
        "ext2spice lvs",
        "ext2spice cthresh 0",
        "ext2spice rthresh 0",
        f"ext2spice -o {OUT_SPICE.name}",
        "quit -noprompt",
        "",
    ])
    proc = subprocess.run(
        [str(MAGIC), "-dnull", "-noconsole", "-rcfile", str(MAGIC_RC)],
        cwd=EXTRACTED, input=commands, text=True, capture_output=True,
        check=False, timeout=90, env={**os.environ, "PDK_ROOT": str(PDK)},
    )
    output = proc.stdout + proc.stderr
    counts = re.findall(r"Total DRC errors found:\s*(\d+)", output, flags=re.IGNORECASE)
    extracted_lines = OUT_SPICE.read_text(encoding="utf-8").splitlines() if OUT_SPICE.exists() else []
    header_lines: list[str] = []
    if extracted_lines:
        for line in extracted_lines:
            if line.startswith(".subckt") or (header_lines and line.startswith("+")):
                header_lines.append(line)
            elif header_lines:
                break
    header = "\n".join(header_lines)
    report = {
        "result_type": "sky130_leaky_ultra_sense_frontend_physical",
        "status": "leaky_frontend_drc_extract_passed_not_leakage_integrated" if proc.returncode == 0 and counts and int(counts[-1]) == 0 and all(name in header for name in REGIONS) else "leaky_frontend_physical_check_incomplete",
        "source_layout": str(SOURCE_CELL.relative_to(ROOT)),
        "derived_layout": str(MAG.relative_to(ROOT)),
        "extracted_netlist": str(OUT_SPICE.relative_to(ROOT)),
        "exposed_regions": list(REGIONS),
        "drc_errors": int(counts[-1]) if counts else None,
        "magic_returncode": proc.returncode,
        "extracted_subckt_header": header,
        "sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in (("layout.mag", MAG), ("extracted.spice", OUT_SPICE)) if path.exists()},
        "accepted_post_layout_written": False,
        "claim_boundary": "Derived physical frontend exposes floating regions for explicit-leakage study; it does not yet prove resistor geometry, full frontend LVS, extracted transient, or converter acceptance.",
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"drc_errors,{report['drc_errors']}")
    print(f"subckt,{header}")
    print(f"json,{OUT}")
    return 0 if report["status"] == "leaky_frontend_drc_extract_passed_not_leakage_integrated" else 1


if __name__ == "__main__":
    raise SystemExit(main())
