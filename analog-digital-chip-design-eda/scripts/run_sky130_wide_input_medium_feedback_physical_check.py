#!/usr/bin/env python3
from __future__ import annotations
import json, os, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench"
CELL = "sky130_latch_precharge_wide_input_medium_feedback_flat"
CELLS, EXT_DIR = WB / "cells", WB / "extracted"
EXT, SPICE = CELLS / f"{CELL}.ext", EXT_DIR / f"{CELL}_extracted.spice"
MAGIC = Path(os.environ.get("MAGIC_BIN", str(Path.home()/"eda-tools/magic-8.3.682/bin/magic")))
PDK = Path(os.environ.get("PDK_ROOT", str(Path.home()/"eda-tools/pdks")))
RC = Path(os.environ.get("MAGIC_RC", str(PDK/"sky130A/libs.tech/magic/sky130A.magicrc")))
OUT = ROOT / "evidence/aimc-simulator-adapters/sky130-wide-input-medium-feedback-physical-check.json"

def main() -> int:
    subprocess.run(["python3", str(ROOT/"scripts/build_sky130_wide_input_medium_feedback_variant.py")], cwd=ROOT, check=True)
    cmd="\n".join([f"path search +{CELLS}",f"load {CELL} -force","select top cell","drc on","drc catchup","drc count","extract all","ext2spice lvs","ext2spice cthresh 0","ext2spice rthresh 0",f"ext2spice -o {SPICE.name}","quit -noprompt",""])
    p=subprocess.run([str(MAGIC),"-dnull","-noconsole","-rcfile",str(RC)],cwd=EXT_DIR,input=cmd,text=True,capture_output=True,check=False,env={**os.environ,"PDK_ROOT":str(PDK)},timeout=120)
    t=EXT.read_text(encoding="utf-8",errors="replace") if EXT.exists() else ""
    ds=[x for x in t.splitlines() if x.startswith("device msubckt sky130_fd_pr__nfet_01v8")]
    ps=[x for x in t.splitlines() if x.startswith("device msubckt sky130_fd_pr__pfet_01v8")]
    m=re.findall(r"Total DRC errors found:\s*(\d+)",p.stdout+p.stderr,re.I); drc=int(m[-1]) if m else None
    feedback=any('"out_p"' in x and '"out_n"' in x for x in ds)
    report={"result_type":"sky130_wide_input_medium_feedback_physical_check","status":"wide_input_medium_feedback_extracted_drc_clean_not_transient_or_converter_signoff" if p.returncode==0 and drc==0 and len(ds)==4 and len(ps)==2 and feedback else "wide_input_medium_feedback_incomplete","layout":str((CELLS/f"{CELL}.mag").relative_to(ROOT)),"extracted":str(SPICE.relative_to(ROOT)),"drc_error_count":drc,"nfet_device_count":len(ds),"pfet_device_count":len(ps),"feedback_present":feedback,"feedback_gate_length_target":"1.33x nominal poly width","accepted_post_layout_written":False}
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"status,{report['status']}"); print(f"drc_errors,{drc}"); print(f"json,{OUT}")
    return 0 if report["status"].endswith("signoff") else 1
if __name__ == "__main__": raise SystemExit(main())
