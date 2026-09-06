#!/usr/bin/env python3
"""DRC/extract the real Sky130 clocked-tail NMOS starter."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench"
CELLS, EXT_DIR = WB / "cells", WB / "extracted"
CELL = "sky130_clocked_tail_switch_starter"
EXT, SPICE = CELLS / f"{CELL}.ext", EXT_DIR / f"{CELL}_extracted.spice"
MAGIC = Path(os.environ.get("MAGIC_BIN", str(Path.home()/"eda-tools/magic-8.3.682/bin/magic")))
PDK = Path(os.environ.get("PDK_ROOT", str(Path.home()/"eda-tools/pdks")))
RC = Path(os.environ.get("MAGIC_RC", str(PDK/"sky130A/libs.tech/magic/sky130A.magicrc")))
OUT = ROOT / "evidence/aimc-simulator-adapters/sky130-clocked-tail-switch-physical-check.json"
MD = ROOT / "evidence/aimc-simulator-adapters/sky130-clocked-tail-switch-physical-check.md"

def main() -> int:
    cmd = "\n".join([f"path search +{CELLS}", f"load {CELL} -force", "select top cell", "drc on", "drc catchup", "drc count", "extract all", "ext2spice lvs", "ext2spice cthresh 0", "ext2spice rthresh 0", f"ext2spice -o {SPICE.name}", "quit -noprompt", ""])
    p = subprocess.run([str(MAGIC), "-dnull", "-noconsole", "-rcfile", str(RC)], cwd=EXT_DIR, input=cmd, text=True, capture_output=True, check=False, env={**os.environ, "PDK_ROOT": str(PDK)}, timeout=120)
    t = EXT.read_text(encoding="utf-8", errors="replace") if EXT.exists() else ""
    ds = [x for x in t.splitlines() if x.startswith("device msubckt sky130_fd_pr__nfet_01v8")]
    nets = {n: any(f'"{n}"' in x for x in ds) or any(f'"{n}"' in x for x in t.splitlines() if x.startswith(("port ", "equiv "))) for n in ("vss", "tail", "eval")}
    m = re.findall(r"Total DRC errors found:\s*(\d+)", p.stdout + p.stderr, re.I)
    drc = int(m[-1]) if m else None
    passed = p.returncode == 0 and drc == 0 and SPICE.exists() and len(ds) == 1 and all(nets.values())
    report = {"result_type": "sky130_clocked_tail_switch_physical_check", "status": "clocked_tail_switch_extracted_drc_clean_not_latch_or_converter_signoff" if passed else "clocked_tail_switch_incomplete", "layout": str((CELLS / f"{CELL}.mag").relative_to(ROOT)), "extracted": str(SPICE.relative_to(ROOT)), "drc_error_count": drc, "nfet_device_count": len(ds), "named_net_presence": nets, "accepted_post_layout_written": False, "claim_boundary": {"allowed": "shows one real Sky130 NMOS tail-switch geometry extracts with vss, tail, and eval connections", "not_allowed": "does not prove integrated latch evaluation timing, transient polarity, noise, mismatch, LVS, PVT yield, SAR conversion, or converter acceptance"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD.write_text("\n".join(["# Sky130 Clocked Tail Switch Physical Check", "", f"- status: `{report['status']}`", f"- DRC errors: `{drc}`", f"- extracted NMOS devices: `{len(ds)}`", f"- named nets: `{nets}`", "", "This is a real-device clocked-tail starter for the latch evaluation phase. It remains separate until integrated routing and extracted transient evidence are complete.", "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"drc_errors,{drc}")
    print(f"json,{OUT}")
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
