#!/usr/bin/env python3
"""Verify the physical passive-to-active sense handoff in the composite cell."""

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
CELL = "sky130_ultra_frontend_active_pair_flat"
EXTRACTED = EXTRACT_DIR / f"{CELL}_extracted.spice"
EXT = CELL_DIR / f"{CELL}.ext"
MAGIC_BIN = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools" / "magic-8.3.682" / "bin" / "magic")))
PDK_ROOT = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools" / "pdks")))
MAGIC_RC = Path(os.environ.get("MAGIC_RC", str(PDK_ROOT / "sky130A" / "libs.tech" / "magic" / "sky130A.magicrc")))
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-ultra-frontend-active-pair-physical-handoff.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-ultra-frontend-active-pair-physical-handoff.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def main() -> int:
    commands = "\n".join([
        f"path search +{CELL_DIR}", f"load {CELL} -force", "select top cell",
        "drc on", "drc catchup", "drc count", "extract all", "ext2spice lvs",
        "ext2spice cthresh 0", "ext2spice rthresh 0", f"ext2spice -o {EXTRACTED.name}",
        "quit -noprompt", "",
    ])
    proc = subprocess.run([
        str(MAGIC_BIN), "-dnull", "-noconsole", "-rcfile", str(MAGIC_RC)
    ], cwd=EXTRACT_DIR, input=commands, text=True, capture_output=True, check=False,
       env={**os.environ, "PDK_ROOT": str(PDK_ROOT)}, timeout=60)
    output = proc.stdout + proc.stderr
    drc_matches = re.findall(r"Total DRC errors found:\s*(\d+)", output, re.IGNORECASE)
    text = EXTRACTED.read_text(encoding="utf-8", errors="replace") if EXTRACTED.exists() else ""
    ext_text = EXT.read_text(encoding="utf-8", errors="replace") if EXT.exists() else ""
    device_lines = [line for line in ext_text.splitlines() if line.startswith("device msubckt sky130_fd_pr__nfet_01v8")]
    gate_sense_p = any('"sense_p"' in line for line in device_lines)
    gate_sense_n = any('"sense_n"' in line for line in device_lines)
    distinct_sense_p_n = len(device_lines) == 2 and gate_sense_p and gate_sense_n
    short_equiv = any('equiv "sense_p" "sense_n"' in line or 'equiv "sense_n" "sense_p"' in line for line in ext_text.splitlines())
    drc_errors = int(drc_matches[-1]) if drc_matches else None
    passed = proc.returncode == 0 and drc_errors == 0 and EXTRACTED.exists() and distinct_sense_p_n and not short_equiv
    report = {
        "result_type": "sky130_ultra_frontend_active_pair_physical_handoff",
        "status": "physical_passive_to_active_handoff_extracted_drc_clean_not_converter_signoff" if passed else "physical_passive_to_active_handoff_incomplete",
        "cell": CELL,
        "layout": rel(CELL_DIR / f"{CELL}.mag"),
        "extracted": rel(EXTRACTED),
        "magic_returncode": proc.returncode,
        "drc_error_count": drc_errors,
        "extracted_exists": EXTRACTED.exists(),
        "active_device_count": len(device_lines),
        "distinct_sense_p_and_sense_n": distinct_sense_p_n,
        "sense_p_gate_found": gate_sense_p,
        "sense_n_gate_found": gate_sense_n,
        "sense_p_sense_n_short_equiv": short_equiv,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "shows the flat physical ultra-sense frontend and transistor isolation pair can be placed together, routed through explicit contact stacks, extracted, and checked for distinct transistor gate connectivity on sense-P and sense-N",
            "not_allowed": "does not prove latch resolution, SAR conversion, full converter LVS, post-layout metrics, robustness, or accepted converter evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join([
        "# Sky130 Ultra Frontend to Active Pair Physical Handoff", "",
        f"- status: `{report['status']}`", f"- cell: `{CELL}`",
        f"- DRC errors: `{drc_errors}`", f"- extracted: `{report['extracted_exists']}`",
        f"- active devices: `{len(device_lines)}`",
        f"- sense-P gate connected: `{gate_sense_p}`",
        f"- sense-N gate connected: `{gate_sense_n}`",
        f"- sense-P/N short equivalence: `{short_equiv}`", "",
        "The flat composite layout places the passive ultra-sense frontend beside the real transistor isolation pair and routes each sense net through explicit contact stacks. Magic extraction records the transistor gates on the named sense-P and sense-N nets without a sense-P/N short. This remains a sub-block result, not full converter acceptance.",
        "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], "",
    ]), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"drc_errors,{drc_errors}")
    print(f"distinct_sense_p_n,{distinct_sense_p_n}")
    print(f"sense_p_gate,{gate_sense_p}")
    print(f"sense_n_gate,{gate_sense_n}")
    print(f"json,{OUT_JSON}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
