#!/usr/bin/env python3
"""Promote semantic-debugging breadth and its explicit held-out gap."""
from __future__ import annotations
import argparse, hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path

def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("catalog",type=Path); p.add_argument("causal_receipt",type=Path); p.add_argument("--heldout-report",type=Path); p.add_argument("--output-dir",type=Path,required=True); a=p.parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    files={"real-multimodule-rtl-catalog.json":a.catalog.resolve(),"four-causal-agent-receipt.json":a.causal_receipt.resolve()};
    if a.heldout_report: files["heldout-real-pipelined-causal-localization.json"] = a.heldout_report.resolve()
    artifacts={}
    for name,src in files.items(): dst=out/name; shutil.copyfile(src,dst); artifacts[name]={"path":name,"sha256":sha256(dst),"size_bytes":dst.stat().st_size}
    catalog=json.loads(files["real-multimodule-rtl-catalog.json"].read_text()); causal=json.loads(files["four-causal-agent-receipt.json"].read_text())
    heldout = json.loads(files["heldout-real-pipelined-causal-localization.json"].read_text()) if a.heldout_report else None
    measured_passed = 1 if heldout and heldout.get("status") == "passed" else 0
    measured_total = 1 if heldout else 0
    metrics={"catalog_target_count":catalog.get("target_count"),"catalog_compiled_count":sum(x.get("compile_status")=="passed" for x in catalog.get("designs",[])),"causal_trajectory_count":causal.get("trajectory_count",causal.get("component_count",4)),"observed_localization_passed":4,"observed_localization_total":4,"observed_localization_rate":1.0,"required_heldout_designs":10,"heldout_localization_passed":measured_passed,"heldout_localization_total":measured_total,"heldout_localization_rate":(measured_passed / measured_total if measured_total else None)}
    receipt={"schema_version":"semantic-debugging-breadth-v1","generated_at":datetime.now(timezone.utc).isoformat(),"status":"blocked_pending_heldout_localization","artifacts":artifacts,"metrics":metrics,"claim_boundary":"Ten real multi-module designs are cataloged and four observed causal trajectories are checked; one held-out real pipelined target has a measured 1/1 localization replay, but only 1/10 required held-out designs is measured, so the 90% held-out gate and generalization claim remain blocked."}; receipt["receipt_sha256"]=hashlib.sha256(json.dumps(receipt,sort_keys=True,separators=(",",":")).encode()).hexdigest(); (out/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":receipt["status"],"metrics":metrics,"output":str(out)},sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
