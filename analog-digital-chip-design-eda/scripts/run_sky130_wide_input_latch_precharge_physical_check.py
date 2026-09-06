#!/usr/bin/env python3
"""DRC/extract the widened-sense physical latch/precharge variant."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
CELL_DIR = WORKBENCH / "cells"
EXTRACT_DIR = WORKBENCH / "extracted"
CELL = "sky130_latch_precharge_wide_input_flat"
OUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-wide-input-latch-precharge-physical-check.json"
MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-wide-input-latch-precharge-physical-check.md"
EXTRACTED = EXTRACT_DIR / f"{CELL}_extracted.spice"
EXT = CELL_DIR / f"{CELL}.ext"
MAGIC_BIN = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools" / "magic-8.3.682" / "bin" / "magic")))
PDK_ROOT = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools" / "pdks")))
MAGIC_RC = Path(os.environ.get("MAGIC_RC", str(PDK_ROOT / "sky130A" / "libs.tech" / "magic" / "sky130A.magicrc")))


def main() -> int:
    subprocess.run(["python3", str(ROOT / "scripts" / "build_sky130_wide_input_latch_precharge_variant.py")], cwd=ROOT, check=True)
    commands = "\n".join([f"path search +{CELL_DIR}", f"load {CELL} -force", "select top cell", "drc on", "drc catchup", "drc count", "extract all", "ext2spice lvs", "ext2spice cthresh 0", "ext2spice rthresh 0", f"ext2spice -o {EXTRACTED.name}", "quit -noprompt", ""])
    proc = subprocess.run([str(MAGIC_BIN), "-dnull", "-noconsole", "-rcfile", str(MAGIC_RC)], cwd=EXTRACT_DIR, input=commands, text=True, capture_output=True, check=False, env={**os.environ, "PDK_ROOT": str(PDK_ROOT)}, timeout=120)
    output = proc.stdout + proc.stderr
    found = re.findall(r"Total DRC errors found:\s*(\d+)", output, re.I)
    ext = EXT.read_text(encoding="utf-8", errors="replace") if EXT.exists() else ""
    nfets = [x for x in ext.splitlines() if x.startswith("device msubckt sky130_fd_pr__nfet_01v8")]
    pfets = [x for x in ext.splitlines() if x.startswith("device msubckt sky130_fd_pr__pfet_01v8")]
    feedback = any('"out_p"' in x and '"out_n"' in x for x in nfets)
    drc = int(found[-1]) if found else None
    passed = proc.returncode == 0 and drc == 0 and EXTRACTED.exists() and len(nfets) == 4 and len(pfets) == 2 and feedback
    report = {"result_type": "sky130_wide_input_latch_precharge_physical_check", "status": "wide_input_latch_precharge_extracted_drc_clean_not_transient_or_converter_signoff" if passed else "wide_input_latch_precharge_incomplete", "layout": str((CELL_DIR / f"{CELL}.mag").relative_to(ROOT)), "extracted": str(EXTRACTED.relative_to(ROOT)), "drc_error_count": drc, "nfet_device_count": len(nfets), "pfet_device_count": len(pfets), "cross_coupled_feedback_present": feedback, "sense_pair_geometry_variant": "diffusion height 600 layout units versus 120 nominal layout units", "accepted_post_layout_written": False, "claim_boundary": {"allowed": "shows the widened-sense six-device physical variant remains DRC-clean and extractable", "not_allowed": "does not prove improved transient polarity, Sky130-model behavior, LVS, noise, mismatch, PVT yield, SAR conversion, or converter acceptance"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD.write_text("\n".join(["# Sky130 Wide-Input Latch plus Precharge Physical Check", "", f"- status: `{report['status']}`", f"- DRC errors: `{drc}`", f"- NMOS devices: `{len(nfets)}`", f"- PMOS devices: `{len(pfets)}`", f"- feedback present: `{feedback}`", "", "This is the measured sizing-target variant: the two sense diffusions are widened symmetrically while feedback and precharge geometry are retained. It remains a candidate until transient and LVS checks pass.", "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"drc_errors,{drc}")
    print(f"json,{OUT}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
