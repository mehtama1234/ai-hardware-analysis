#!/usr/bin/env python3
from __future__ import annotations
import json, os, re, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; WB=ROOT/"labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench"; CELLS,EXT_DIR=WB/"cells",WB/"extracted"; CELL="sky130_latch_precharge_tail_flat"; EXT=CELLS/f"{CELL}.ext"; SPICE=EXT_DIR/f"{CELL}_extracted.spice"
MAGIC=Path(os.environ.get("MAGIC_BIN",str(Path.home()/"eda-tools/magic-8.3.682/bin/magic"))); PDK=Path(os.environ.get("PDK_ROOT",str(Path.home()/"eda-tools/pdks"))); RC=Path(os.environ.get("MAGIC_RC",str(PDK/"sky130A/libs.tech/magic/sky130A.magicrc"))); OUT=ROOT/"evidence/aimc-simulator-adapters/sky130-latch-precharge-tail-flat-physical-check.json"
def main():
 subprocess.run(["python3",str(ROOT/"scripts/build_sky130_latch_precharge_tail_flat.py")],cwd=ROOT,check=True)
 cmd="\n".join([f"path search +{CELLS}",f"load {CELL} -force","select top cell","drc on","drc catchup","drc count","extract all","ext2spice lvs","ext2spice cthresh 0","ext2spice rthresh 0",f"ext2spice -o {SPICE.name}","quit -noprompt",""])
 p=subprocess.run([str(MAGIC),"-dnull","-noconsole","-rcfile",str(RC)],cwd=EXT_DIR,input=cmd,text=True,capture_output=True,check=False,env={**os.environ,"PDK_ROOT":str(PDK)},timeout=120)
 t=EXT.read_text(encoding="utf-8",errors="replace") if EXT.exists() else ""; nf=[x for x in t.splitlines() if x.startswith("device msubckt sky130_fd_pr__nfet_01v8")]; pf=[x for x in t.splitlines() if x.startswith("device msubckt sky130_fd_pr__pfet_01v8")]; nets={n:any(f'"{n}"' in x for x in nf) or any(f'"{n}"' in x for x in t.splitlines() if x.startswith(("port ","equiv "))) for n in ("tail","eval","vss","reset","out_p","out_n")}; m=re.findall(r"Total DRC errors found:\s*(\d+)",p.stdout+p.stderr,re.I); drc=int(m[-1]) if m else None; passed=p.returncode==0 and drc==0 and SPICE.exists() and len(nf)==5 and len(pf)==2 and all(nets.values())
 report={"result_type":"sky130_latch_precharge_tail_flat_physical_check","status":"flat_latch_precharge_tail_extracted_drc_clean_not_transient_or_converter_signoff" if passed else "flat_latch_precharge_tail_incomplete","layout":str((CELLS/f"{CELL}.mag").relative_to(ROOT)),"extracted":str(SPICE.relative_to(ROOT)),"drc_error_count":drc,"nfet_device_count":len(nf),"pfet_device_count":len(pf),"named_net_presence":nets,"accepted_post_layout_written":False}; OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8"); print(f"status,{report['status']}"); print(f"drc_errors,{drc}"); print(f"nfet_device_count,{len(nf)}"); print(f"pfet_device_count,{len(pf)}"); print(f"json,{OUT}"); return 0 if passed else 1
if __name__=="__main__": raise SystemExit(main())
