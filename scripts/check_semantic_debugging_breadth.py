#!/usr/bin/env python3
"""Independently check semantic-debugging breadth without false promotion."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("receipt",type=Path);a=p.parse_args(); rp=a.receipt.resolve(); errors=[]
 try: r=json.loads(rp.read_text()); cat=json.loads((rp.parent/"real-multimodule-rtl-catalog.json").read_text()); causal=json.loads((rp.parent/"four-causal-agent-receipt.json").read_text())
 except (OSError,json.JSONDecodeError) as e: print(json.dumps({"status":"blocked","errors":[str(e)]})); return 1
 if r.get("schema_version")!="semantic-debugging-breadth-v1" or r.get("receipt_sha256")!=digest({k:v for k,v in r.items() if k!="receipt_sha256"}): errors.append("receipt schema or digest mismatch")
 if r.get("status")!="blocked_pending_heldout_localization": errors.append("missing explicit held-out block")
 if cat.get("schema_version")!="real-multimodule-rtl-catalog-v1" or cat.get("target_count")<10 or sum(x.get("compile_status")=="passed" for x in cat.get("designs",[]))<10: errors.append("catalog does not prove ten compiled designs")
 if causal.get("status")!="passed": errors.append("causal receipt is not passed")
 m=r.get("metrics",{});
 if m.get("observed_localization_rate")!=1.0 or m.get("heldout_localization_passed")!=3 or m.get("heldout_localization_total")!=3 or m.get("heldout_localization_rate")!=1.0 or m.get("required_heldout_designs")!=10: errors.append("localization boundary is malformed")
 for name,item in r.get("artifacts",{}).items():
  pth=rp.parent/item.get("path","")
  if not pth.is_file() or sha(pth)!=item.get("sha256"): errors.append(f"artifact digest mismatch: {name}")
  if name.startswith("heldout-real-") and pth.is_file():
   try:
    heldout=json.loads(pth.read_text()); body={k:v for k,v in heldout.items() if k!="report_sha256"}
    if heldout.get("report_sha256")!=digest(body): errors.append("held-out report digest mismatch")
    if not str(heldout.get("schema_version","")).startswith("heldout-real-") or heldout.get("status")!="passed": errors.append("held-out report is not passed")
    if heldout.get("canonical_status")!="passed" or heldout.get("mutated_status")!="failed": errors.append("held-out canonical/mutated statuses are malformed")
    if heldout.get("frontier",{}).get("status")!="diverged" or heldout.get("binding",{}).get("status")!="available" or heldout.get("localization",{}).get("status")!="available": errors.append("held-out causal localization is incomplete")
    if heldout.get("integrity_errors")!=[]: errors.append("held-out report contains integrity errors")
   except (OSError,json.JSONDecodeError): errors.append("held-out report is unreadable")
 if "3/10" not in r.get("claim_boundary","") or "90%" not in r.get("claim_boundary","") or "blocked" not in r.get("claim_boundary","").lower(): errors.append("claim boundary does not preserve held-out limit")
 result={"schema_version":"semantic-debugging-breadth-check-v1","status":"passed" if not errors else "blocked","receipt":str(rp),"metrics":m,"errors":sorted(set(errors))};result["check_sha256"]=digest(result);print(json.dumps(result,sort_keys=True));return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
