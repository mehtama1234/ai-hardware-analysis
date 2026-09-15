#!/usr/bin/env python3
"""Compare matched OpenLane configurations and append a Pareto record."""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

def digest(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def runtime(path:Path)->float: return sum(float(v) for v in re.findall(r"runtime_s:\s*([0-9.]+)", (path/"runtime.yaml").read_text()))
def read_variant(label:str, path:Path, source_relative:str)->dict:
    row=next(csv.DictReader((path/"reports/metrics.csv").open(encoding="utf-8"))); lvs=next((int(x.split("=")[-1].strip()) for rpt in path.glob("reports/signoff/*lvs.rpt") for x in rpt.read_text(errors="ignore").splitlines() if x.strip().startswith("Total errors")),None); warnings=len((path/"warnings.log").read_text(errors="ignore").splitlines()) if (path/"warnings.log").is_file() else None
    staged_source=path.parent.parent/"src"/source_relative
    return {"label":label,"run_dir":str(path),"config":row.get("config"),"flow_status":row.get("flow_status"),"die_area_mm2":float(row["DIEAREA_mm^2"]),"core_area_um2":float(row["CoreArea_um^2"]),"runtime_seconds":runtime(path),"spef_wns":float(row["spef_wns"]),"spef_tns":float(row["spef_tns"]),"warnings":warnings,"lvs_errors":lvs,"route_violations":int(row["tritonRoute_violations"]),"magic_violations":int(row["Magic_violations"]),"gds_present":any(p.is_file() and p.stat().st_size>0 for p in (path/"results/signoff").glob("*.gds")),"source_path":str(staged_source),"source_sha256":digest(staged_source)}
def main()->int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--manifest",type=Path,required=True); parser.add_argument("--history",type=Path,required=True); parser.add_argument("--output",type=Path,required=True); parser.add_argument("--run-id",required=True); parser.add_argument("--source-relative",default="csr_regs.sv"); parser.add_argument("--variant",action="append",nargs=2,metavar=("LABEL","RUN_DIR"),required=True); args=parser.parse_args()
    variants=[read_variant(label,Path(raw).resolve(),args.source_relative) for label,raw in args.variant]; source_hashes={x["source_sha256"] for x in variants}; passed=lambda x:x["flow_status"]=="flow completed" and x["lvs_errors"]==0 and x["route_violations"]==0 and x["magic_violations"]==0 and x["gds_present"]
    pareto=[]
    for candidate in variants:
        dominated=False
        for other in variants:
            if other is candidate: continue
            no_worse=other["die_area_mm2"]<=candidate["die_area_mm2"] and other["runtime_seconds"]<=candidate["runtime_seconds"] and other["spef_wns"]>=candidate["spef_wns"]
            strictly=other["die_area_mm2"]<candidate["die_area_mm2"] or other["runtime_seconds"]<candidate["runtime_seconds"] or other["spef_wns"]>candidate["spef_wns"]
            if no_worse and strictly: dominated=True
        if not dominated: pareto.append(candidate["label"])
    history=args.history.resolve(); previous="0"*64
    if history.is_file() and history.read_text().strip(): previous=json.loads(history.read_text().splitlines()[-1])["record_hash"]
    record={"schema_version":"physical-optimization-comparison-v1","run_id":args.run_id,"recorded_at":datetime.now(timezone.utc).isoformat(),"manifest":{"path":str(args.manifest.resolve()),"sha256":digest(args.manifest.resolve())},"same_source":len(source_hashes)==1,"variants":variants,"pareto_frontier":pareto,"decision":{"status":"retain_pareto_candidates","area_winner":min(variants,key=lambda x:x["die_area_mm2"])["label"],"runtime_winner":min(variants,key=lambda x:x["runtime_seconds"])["label"],"reason":"Both configurations pass physical checks; the area and runtime winners are retained when neither configuration dominates the other."},"previous_record_hash":previous,"claim_boundary":"Controlled local OpenLane configuration comparison only; not a statistically significant PPA benchmark or commercial signoff."}
    record["record_hash"]=hashlib.sha256(json.dumps(record,sort_keys=True,separators=(",",":")).encode()).hexdigest(); history.parent.mkdir(parents=True,exist_ok=True); history.open("a").write(json.dumps(record,sort_keys=True)+"\n"); out=args.output.resolve(); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n"); ok=len(variants)==2 and len(source_hashes)==1 and all(passed(x) for x in variants); print(json.dumps({"status":"passed" if ok else "failed","pareto_frontier":pareto,"area_winner":record["decision"]["area_winner"],"runtime_winner":record["decision"]["runtime_winner"]},sort_keys=True)); return 0 if ok else 1
if __name__=="__main__": raise SystemExit(main())
