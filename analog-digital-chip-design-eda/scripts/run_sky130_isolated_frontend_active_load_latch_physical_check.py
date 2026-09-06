#!/usr/bin/env python3
"""DRC/extract the isolation-pair plus active-load latch composition."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from audit_isolated_latch_connectivity import audit, audit_substrate_capacitance

ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench"
CELLS, EXTRACTED_DIR = WB / "cells", WB / "extracted"
CELL = "sky130_isolated_frontend_active_load_latch_v2"
EXT = CELLS / f"{CELL}.ext"
SPICE = EXTRACTED_DIR / f"{CELL}_extracted.spice"
MAGIC = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools/magic-8.3.682/bin/magic")))
PDK = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools/pdks")))
RC = Path(os.environ.get("MAGIC_RC", str(PDK / "sky130A/libs.tech/magic/sky130A.magicrc")))
OUT = ROOT / "evidence/aimc-simulator-adapters/sky130-isolated-frontend-active-load-latch-v2-physical-check.json"


def main() -> int:
    subprocess.run(["python3", str(ROOT / "scripts/build_sky130_isolated_frontend_active_load_latch.py")], cwd=ROOT, check=True)
    commands = "\n".join([
        f"path search +{CELLS}", f"load {CELL} -force", "select top cell", "drc on", "drc catchup",
        "drc count", "extract all", "ext2spice lvs", "ext2spice hierarchy off",
        "ext2spice subcircuit on", "ext2spice subcircuit top on",
        "ext2spice cthresh 0", "ext2spice rthresh 0",
        f"ext2spice -o {SPICE.name}", "quit -noprompt", "",
    ])
    proc = subprocess.run([str(MAGIC), "-dnull", "-noconsole", "-rcfile", str(RC)], cwd=EXTRACTED_DIR,
                          input=commands, text=True, capture_output=True, check=False,
                          env={**os.environ, "PDK_ROOT": str(PDK)}, timeout=120)
    text = EXT.read_text(encoding="utf-8", errors="replace") if EXT.exists() else ""
    nf = [x for x in text.splitlines() if x.startswith("device msubckt sky130_fd_pr__nfet_01v8")]
    pf = [x for x in text.splitlines() if x.startswith("device msubckt sky130_fd_pr__pfet_01v8")]
    matches = re.findall(r"Total DRC errors found:\s*(\d+)", proc.stdout + proc.stderr, re.I)
    drc = int(matches[-1]) if matches else None
    ports = {n: f'port "{n}"' in text for n in ("sense_p", "sense_n", "out_p", "out_n", "tail", "reset", "eval", "vdd", "vss", "iso_tail")}
    isolator = [x for x in nf if '"sense_p"' in x or '"sense_n"' in x]
    active = [x for x in pf if '"vdd_active"' in x]
    connectivity = audit(SPICE) if SPICE.exists() else {"topology_pass": False, "body_ties_pass": False}
    capacitance = audit_substrate_capacitance(EXT, SPICE) if EXT.exists() and SPICE.exists() else {"pass": False}
    passed = proc.returncode == 0 and drc == 0 and SPICE.exists() and len(nf) == 7 and len(pf) == 4 and all(ports.values()) and len(isolator) == 2 and len(active) == 2 and connectivity["topology_pass"] and connectivity["body_ties_pass"]
    passed = passed and capacitance["pass"]
    report = {
        "result_type": "sky130_isolated_frontend_active_load_latch_physical_check",
        "status": "isolated_frontend_active_load_latch_extracted_drc_clean_not_transient_or_converter_signoff" if passed else "isolated_frontend_active_load_latch_incomplete",
        "layout": str((CELLS / f"{CELL}.mag").relative_to(ROOT)),
        "extracted": str(SPICE.relative_to(ROOT)), "drc_error_count": drc,
        "nfet_device_count": len(nf), "pfet_device_count": len(pf), "named_net_presence": ports,
        "isolator_input_device_count": len(isolator), "active_load_device_count": len(active),
        "accepted_post_layout_written": False,
        "connectivity": connectivity,
        "output_capacitance_export": capacitance,
        "extraction_hierarchy": "off; flat geometry with explicit subcircuit wrapper",
        "claim_boundary": "physical composition and extraction only; not transient, offset, noise, PVT, SAR, or converter acceptance",
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}"); print(f"drc_errors,{drc}"); print(f"nfet_device_count,{len(nf)}"); print(f"pfet_device_count,{len(pf)}"); print(f"json,{OUT}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
