#!/usr/bin/env python3
"""DRC/extract the matched PMOS precharge pair starter."""

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
CELL = "sky130_pmos_precharge_pair_starter"
EXTRACTED = EXTRACT_DIR / f"{CELL}_extracted.spice"
EXT = CELL_DIR / f"{CELL}.ext"
MAGIC_BIN = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools" / "magic-8.3.682" / "bin" / "magic")))
PDK_ROOT = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools" / "pdks")))
MAGIC_RC = Path(os.environ.get("MAGIC_RC", str(PDK_ROOT / "sky130A" / "libs.tech" / "magic" / "sky130A.magicrc")))
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-pmos-precharge-pair-physical-check.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-pmos-precharge-pair-physical-check.md"


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def main() -> int:
    commands = "\n".join([f"path search +{CELL_DIR}", f"load {CELL} -force", "select top cell", "drc on", "drc catchup", "drc count", "extract all", "ext2spice lvs", "ext2spice cthresh 0", "ext2spice rthresh 0", f"ext2spice -o {EXTRACTED.name}", "quit -noprompt", ""])
    proc = subprocess.run([str(MAGIC_BIN), "-dnull", "-noconsole", "-rcfile", str(MAGIC_RC)], cwd=EXTRACT_DIR, input=commands, text=True, capture_output=True, check=False, env={**os.environ, "PDK_ROOT": str(PDK_ROOT)}, timeout=60)
    output = proc.stdout + proc.stderr
    matches = re.findall(r"Total DRC errors found:\s*(\d+)", output, re.I)
    ext_text = EXT.read_text(encoding="utf-8", errors="replace") if EXT.exists() else ""
    devices = [line for line in ext_text.splitlines() if line.startswith("device msubckt sky130_fd_pr__pfet_01v8")]
    nets = {name: any(f'"{name}"' in line for line in devices) or any(f'"{name}"' in line for line in ext_text.splitlines() if line.startswith(("port ", "equiv "))) for name in ("vdd", "precharge_p", "precharge_n", "reset")}
    drc = int(matches[-1]) if matches else None
    passed = proc.returncode == 0 and drc == 0 and EXTRACTED.exists() and len(devices) == 2 and all(nets.values())
    report = {"result_type": "sky130_pmos_precharge_pair_physical_check", "status": "pmos_precharge_pair_extracted_drc_clean_not_latch_or_converter_signoff" if passed else "pmos_precharge_pair_incomplete", "cell": CELL, "layout": rel(CELL_DIR / f"{CELL}.mag"), "extracted": rel(EXTRACTED), "drc_error_count": drc, "pmos_device_count": len(devices), "named_net_presence": nets, "accepted_post_layout_written": False, "claim_boundary": {"allowed": "shows two real Sky130 PMOS geometries with separate precharge outputs, common supply, and reset-gate labels can be extracted cleanly", "not_allowed": "does not prove integrated latch routing, reset timing, transient regeneration, noise, mismatch, LVS, PVT yield, SAR conversion, or converter acceptance"}}
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(["# Sky130 PMOS Precharge Pair Physical Check", "", f"- status: `{report['status']}`", f"- DRC errors: `{drc}`", f"- extracted PMOS devices: `{len(devices)}`", f"- named nets: `{nets}`", "", "This is a matched PMOS precharge physical starter for the latch reset phase. It is separate from the latch until an integrated parent route and extracted transient are demonstrated.", "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"drc_errors,{drc}")
    print(f"pmos_device_count,{len(devices)}")
    print(f"json,{OUT_JSON}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
