#!/usr/bin/env python3
"""DRC/extract the flat physical latch plus PMOS precharge parent."""

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
CELL = "sky130_latch_precharge_flat"
EXT = CELL_DIR / f"{CELL}.ext"
EXTRACTED = EXTRACT_DIR / f"{CELL}_extracted.spice"
MAGIC_BIN = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools" / "magic-8.3.682" / "bin" / "magic")))
PDK_ROOT = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools" / "pdks")))
MAGIC_RC = Path(os.environ.get("MAGIC_RC", str(PDK_ROOT / "sky130A" / "libs.tech" / "magic" / "sky130A.magicrc")))
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-latch-precharge-flat-physical-check.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-latch-precharge-flat-physical-check.md"


def main() -> int:
    subprocess.run(["python3", str(ROOT / "scripts" / "build_sky130_latch_precharge_flat.py")], cwd=ROOT, check=True)
    commands = "\n".join([f"path search +{CELL_DIR}", f"load {CELL} -force", "select top cell", "drc on", "drc catchup", "drc count", "extract all", "ext2spice lvs", "ext2spice cthresh 0", "ext2spice rthresh 0", f"ext2spice -o {EXTRACTED.name}", "quit -noprompt", ""])
    proc = subprocess.run([str(MAGIC_BIN), "-dnull", "-noconsole", "-rcfile", str(MAGIC_RC)], cwd=EXTRACT_DIR, input=commands, text=True, capture_output=True, check=False, env={**os.environ, "PDK_ROOT": str(PDK_ROOT)}, timeout=120)
    output = proc.stdout + proc.stderr
    found = re.findall(r"Total DRC errors found:\s*(\d+)", output, re.I)
    ext = EXT.read_text(encoding="utf-8", errors="replace") if EXT.exists() else ""
    nfets = [x for x in ext.splitlines() if x.startswith("device msubckt sky130_fd_pr__nfet_01v8")]
    pfets = [x for x in ext.splitlines() if x.startswith("device msubckt sky130_fd_pr__pfet_01v8")]
    equiv = [x for x in ext.splitlines() if x.startswith("equiv ")]
    feedback = any('"out_p"' in x and '"out_n"' in x for x in nfets)
    precharge = len(pfets) == 2 and any('"reset"' in x for x in pfets)
    outputs = any('"out_p"' in x for x in nfets) and any('"out_n"' in x for x in nfets)
    drc = int(found[-1]) if found else None
    passed = proc.returncode == 0 and drc == 0 and EXTRACTED.exists() and len(nfets) == 4 and len(pfets) == 2 and feedback and precharge and outputs
    report = {"result_type": "sky130_latch_precharge_flat_physical_check", "status": "flat_latch_precharge_extracted_drc_clean_not_transient_or_converter_signoff" if passed else "flat_latch_precharge_incomplete", "layout": str((CELL_DIR / f"{CELL}.mag").relative_to(ROOT)), "extracted": str(EXTRACTED.relative_to(ROOT)), "drc_error_count": drc, "nfet_device_count": len(nfets), "pfet_device_count": len(pfets), "cross_coupled_feedback_present": feedback, "precharge_pair_present": precharge, "named_output_domains_present": outputs, "equivalences": equiv, "accepted_post_layout_written": False, "claim_boundary": {"allowed": "shows the latch and physical PMOS precharge pair are flattened, DRC-clean, and extracted together with four NMOS feedback devices and two PMOS reset devices", "not_allowed": "does not prove clocked transient regeneration, Sky130-model convergence, noise, mismatch, LVS against a schematic, PVT yield, SAR conversion, or converter acceptance"}}
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(["# Sky130 Flat Latch plus PMOS Precharge Physical Check", "", f"- status: `{report['status']}`", f"- DRC errors: `{drc}`", f"- NMOS devices: `{len(nfets)}`", f"- PMOS devices: `{len(pfets)}`", f"- cross-coupled feedback present: `{feedback}`", f"- PMOS precharge pair present: `{precharge}`", "", "The latch and PMOS precharge pair are flattened into one physical parent and checked by Magic. This remains a physical integration artifact until an extracted Sky130 clocked transient and matching LVS are complete.", "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"drc_errors,{drc}")
    print(f"nfet_device_count,{len(nfets)}")
    print(f"pfet_device_count,{len(pfets)}")
    print(f"json,{OUT_JSON}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
