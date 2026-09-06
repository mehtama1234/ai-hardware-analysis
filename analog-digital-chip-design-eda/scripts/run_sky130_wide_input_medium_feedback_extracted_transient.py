#!/usr/bin/env python3
from __future__ import annotations
import json,re,subprocess
from pathlib import Path
import run_sky130_flat_latch_precharge_extracted_transient as base

ROOT=base.ROOT; CELL="sky130_latch_precharge_wide_input_medium_feedback_flat"
base.EXTRACTED=base.LAB/"layout-workbench"/"extracted"/f"{CELL}_extracted.spice"
base.DECK=base.LAB/"spice"/"sky130-wide-input-medium-feedback-extracted-transient.sp"
OUT=ROOT/"evidence/aimc-simulator-adapters/sky130-wide-input-medium-feedback-extracted-transient.json"
def main()->int:
 rows=[]
 for diff in (-10.0,-0.5,0.5,10.0):
  base.DECK.write_text(base.make_deck(diff).replace("sky130_latch_precharge_flat",CELL),encoding="utf-8")
  p=subprocess.run(["ngspice","-b",str(base.DECK)],cwd=ROOT,text=True,capture_output=True,check=False,timeout=30)
  row={"input_diff_mv":diff,"measured":p.returncode==0,"returncode":p.returncode}
  if p.returncode==0:
   v=re.findall(r"output_diff_final\s*=\s*([-+0-9.eE]+)",p.stdout); row["output_diff_final_v"]=float(v[-1]) if v else None; row["polarity_pass"]=row["output_diff_final_v"] is not None and ((row["output_diff_final_v"]<0)==(diff>0)); row["regenerated"]=row["output_diff_final_v"] is not None and abs(row["output_diff_final_v"])>=0.5
  else: row["error_excerpt"]=(p.stdout+p.stderr)[-1000:]
  rows.append(row)
 measured=[r for r in rows if r["measured"]]; passing=[r for r in measured if r.get("polarity_pass") and r.get("regenerated")]
 report={"result_type":"sky130_wide_input_medium_feedback_extracted_transient","status":"wide_input_medium_feedback_transient_passed_not_sky130_model_or_converter_signoff" if len(passing)==len(rows) else "wide_input_medium_feedback_transient_open","cell":CELL,"case_count":len(rows),"measured_case_count":len(measured),"passing_case_count":len(passing),"rows":rows,"accepted_post_layout_written":False}
 OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8"); print(f"status,{report['status']}"); print(f"passing_case_count,{len(passing)}"); print(f"json,{OUT}"); return 0 if len(passing)==len(rows) else 1
if __name__=="__main__": raise SystemExit(main())
