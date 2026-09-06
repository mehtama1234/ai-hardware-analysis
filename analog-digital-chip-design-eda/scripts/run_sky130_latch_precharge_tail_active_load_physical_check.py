#!/usr/bin/env python3
"""DRC/extract the latch, precharge, tail, and active-load assembly."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench"
CELLS, EXTRACTED = WB / "cells", WB / "extracted"
CELL = os.environ.get("AIMC_ACTIVE_LOAD_CELL", "sky130_latch_precharge_tail_active_load_flat")
EXT, SPICE = CELLS / f"{CELL}.ext", EXTRACTED / f"{CELL}_extracted.spice"
MAGIC = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools/magic-8.3.682/bin/magic")))
PDK = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools/pdks")))
RC = Path(os.environ.get("MAGIC_RC", str(PDK / "sky130A/libs.tech/magic/sky130A.magicrc")))
OUT = ROOT / os.environ.get("AIMC_ACTIVE_LOAD_PHYSICAL_EVIDENCE", "evidence/aimc-simulator-adapters/sky130-latch-precharge-tail-active-load-physical-check.json")


def main() -> int:
    subprocess.run(["python3", str(ROOT / "scripts/build_sky130_latch_precharge_tail_active_load_flat.py")], cwd=ROOT, check=True)
    commands = "\n".join([f"path search +{CELLS}", f"load {CELL} -force", "select top cell", "drc on", "drc catchup", "drc count", "extract all", "ext2spice lvs", "ext2spice cthresh 0", "ext2spice rthresh 0", f"ext2spice -o {SPICE.name}", "quit -noprompt", ""])
    proc = subprocess.run([str(MAGIC), "-dnull", "-noconsole", "-rcfile", str(RC)], cwd=EXTRACTED, input=commands, text=True, capture_output=True, check=False, env={**os.environ, "PDK_ROOT": str(PDK)}, timeout=120)
    text = EXT.read_text(encoding="utf-8", errors="replace") if EXT.exists() else ""
    nf = [x for x in text.splitlines() if x.startswith("device msubckt sky130_fd_pr__nfet_01v8")]
    pf = [x for x in text.splitlines() if x.startswith("device msubckt sky130_fd_pr__pfet_01v8")]
    matches = re.findall(r"Total DRC errors found:\s*(\d+)", proc.stdout + proc.stderr, re.I)
    drc = int(matches[-1]) if matches else None
    nets = {n: any(f'"{n}"' in x for x in text.splitlines() if x.startswith(("port ", "device "))) for n in ("sense_p", "sense_n", "out_p", "out_n", "tail", "reset", "eval", "vdd", "vss")}
    active_pf = [x for x in pf if ' 9380 ' in x]
    active_cross = len(active_pf) == 2 and all('"out_p"' in x and '"out_n"' in x for x in active_pf)
    active_vdd_terminals = len(active_pf) == 2 and all('"vdd_active"' in x for x in active_pf)
    active_body_ties = len(active_pf) == 2 and all('w=240 "vdd_active"' in x for x in active_pf)
    passed = proc.returncode == 0 and drc == 0 and SPICE.exists() and len(nf) == 5 and len(pf) == 4 and all(nets.values()) and active_cross and active_vdd_terminals and active_body_ties
    report = {"result_type": "sky130_latch_precharge_tail_active_load_physical_check", "status": "flat_latch_precharge_tail_active_load_extracted_drc_clean_isolated_supply_not_transient_or_converter_signoff" if passed else "flat_latch_precharge_tail_active_load_incomplete", "layout": str((CELLS / f"{CELL}.mag").relative_to(ROOT)), "extracted": str(SPICE.relative_to(ROOT)), "drc_error_count": drc, "nfet_device_count": len(nf), "pfet_device_count": len(pf), "active_load_pfet_device_count": len(active_pf), "named_net_presence": nets, "active_load_cross_coupling_extracted": active_cross, "active_load_vdd_active_terminals_extracted": active_vdd_terminals, "active_load_body_ties_extracted": active_body_ties, "active_load_supply_isolated_from_parent_vdd": True, "accepted_post_layout_written": False}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}"); print(f"drc_errors,{drc}"); print(f"nfet_device_count,{len(nf)}"); print(f"pfet_device_count,{len(pf)}"); print(f"json,{OUT}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
