#!/usr/bin/env python3
"""Run DRC and Magic extraction for the cross-coupled PMOS load starter."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
CELLS, EXTRACTED_DIR = WORKBENCH / "cells", WORKBENCH / "extracted"
CELL = "sky130_cross_coupled_pmos_load_pair_starter"
EXT = CELLS / f"{CELL}.ext"
SPICE = EXTRACTED_DIR / f"{CELL}_extracted.spice"
MAGIC = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools" / "magic-8.3.682" / "bin" / "magic")))
PDK = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools" / "pdks")))
RC = Path(os.environ.get("MAGIC_RC", str(PDK / "sky130A" / "libs.tech" / "magic" / "sky130A.magicrc")))
OUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-cross-coupled-pmos-load-pair-physical-check.json"


def main() -> int:
    subprocess.run(["python3", str(ROOT / "scripts" / "build_sky130_cross_coupled_pmos_load_pair.py")], cwd=ROOT, check=True)
    commands = "\n".join([f"path search +{CELLS}", f"load {CELL} -force", "select top cell", "drc on", "drc catchup", "drc count", "extract all", "ext2spice lvs", "ext2spice cthresh 0", "ext2spice rthresh 0", f"ext2spice -o {SPICE.name}", "quit -noprompt", ""])
    proc = subprocess.run([str(MAGIC), "-dnull", "-noconsole", "-rcfile", str(RC)], cwd=EXTRACTED_DIR, input=commands, text=True, capture_output=True, check=False, env={**os.environ, "PDK_ROOT": str(PDK)}, timeout=120)
    ext_text = EXT.read_text(encoding="utf-8", errors="replace") if EXT.exists() else ""
    devices = [line for line in ext_text.splitlines() if line.startswith("device msubckt sky130_fd_pr__pfet_01v8")]
    drc_matches = re.findall(r"Total DRC errors found:\s*(\d+)", proc.stdout + proc.stderr, re.I)
    drc = int(drc_matches[-1]) if drc_matches else None
    cross = any('"out_p"' in line and '"out_n"' in line for line in devices) and any('"out_n"' in line and '"out_p"' in line for line in devices)
    common_vdd = sum('"vdd"' in line for line in devices) == 2
    passed = proc.returncode == 0 and drc == 0 and SPICE.exists() and len(devices) == 2 and cross and common_vdd
    report = {"result_type": "sky130_cross_coupled_pmos_load_pair_physical_check", "status": "cross_coupled_pmos_load_pair_extracted_drc_clean_not_latch_or_converter_signoff" if passed else "cross_coupled_pmos_load_pair_incomplete", "layout": str((CELLS / f"{CELL}.mag").relative_to(ROOT)), "extracted": str(SPICE.relative_to(ROOT)), "drc_error_count": drc, "pfet_device_count": len(devices), "cross_coupled_output_gate_nets_present": cross, "common_vdd_present": common_vdd, "accepted_post_layout_written": False}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"drc_errors,{drc}")
    print(f"pfet_device_count,{len(devices)}")
    print(f"json,{OUT}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
