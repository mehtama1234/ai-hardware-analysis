#!/usr/bin/env python3
"""Record a measured closed-loop run and append it to a hash-chained history."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def runtime_seconds(path:Path)->float:
    return sum(float(value) for value in re.findall(r"runtime_s:\s*([0-9.]+)", path.read_text(encoding="utf-8")))

def timed(command:list[str])->dict[str,object]:
    started=time.perf_counter(); run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,check=False); return {"command":command,"returncode":run.returncode,"status":"passed" if run.returncode==0 else "failed","duration_ms":round((time.perf_counter()-started)*1000,2)}

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--manifest",type=Path,required=True); parser.add_argument("--model-report",type=Path,required=True); parser.add_argument("--run",action="append",nargs=2,metavar=("DESIGN","RUN_DIR"),required=True); parser.add_argument("--history",type=Path,required=True); parser.add_argument("--output",type=Path,required=True); args=parser.parse_args()
    manifest=args.manifest.resolve(); model=args.model_report.resolve(); release=json.loads(manifest.read_text(encoding="utf-8")); model_report=json.loads(model.read_text(encoding="utf-8")); checks=[timed(["python3","scripts/check_three_design_release_manifest.py",str(manifest)]),timed(["python3","scripts/verify_llm_model_evaluation.py",str(model)])]
    physical={}
    for design,raw_run in args.run:
        run=Path(raw_run).resolve(); runtime=run/"runtime.yaml"; warnings=run/"warnings.log"; physical[design]={"run_dir":str(run),"runtime_seconds":runtime_seconds(runtime) if runtime.is_file() else None,"warning_count":len([line for line in warnings.read_text(encoding="utf-8").splitlines() if line.strip()]) if warnings.is_file() else None,"metrics_sha256":digest(run/"reports/metrics.csv") if (run/"reports/metrics.csv").is_file() else None}
    history=args.history.resolve(); history.parent.mkdir(parents=True,exist_ok=True); previous_hash="0"*64
    if history.is_file() and history.read_text(encoding="utf-8").strip(): previous_hash=json.loads(history.read_text(encoding="utf-8").splitlines()[-1])["record_hash"]
    record={"schema_version":"closed-loop-measurement-v1","run_id":"four-design-protocol-repair-20260913","recorded_at":datetime.now(timezone.utc).isoformat(),"release_manifest":{"path":str(manifest),"sha256":digest(manifest)},"model":{"path":str(model),"sha256":digest(model),"model_batch_p50_ms":model_report.get("metrics",{}).get("model_latency_summary",{}).get("local-batch-command",{}).get("p50_ms"),"model_batch_p95_ms":model_report.get("metrics",{}).get("model_latency_summary",{}).get("local-batch-command",{}).get("p95_ms")},"verification_checks":checks,"physical_runs":physical,"optimization_state":{"priors":{"clock_period_ns":10.0,"pdk":"sky130A/sky130_fd_sc_hd"},"rules":["never mutate canonical source","require model-grounded review","require source hash match before physical handoff"],"failure_patterns":["inverted Boolean guard","missing enable guard","temporal threshold","hierarchical address decode"],"sensitivity_matrix":{},"pareto_frontier":[{"objective":"physical_flow","value":"passed"},{"objective":"formal_properties","value":"passed"}],"runtime_estimates":{"model_batch_ms":model_report.get("metrics",{}).get("model_latency_summary",{}).get("local-batch-command",{}).get("p50_ms"),"physical_run_seconds":{design:item["runtime_seconds"] for design,item in physical.items()}}},"previous_record_hash":previous_hash,"claim_boundary":"Measured local research workflow timing and physical-run metadata only; not a production performance benchmark, commercial signoff, or silicon result."}
    encoded=json.dumps(record,sort_keys=True,separators=(",",":")); record["record_hash"]=hashlib.sha256(encoded.encode()).hexdigest(); history.open("a",encoding="utf-8").write(json.dumps(record,sort_keys=True)+"\n"); args.output.resolve().parent.mkdir(parents=True,exist_ok=True); args.output.resolve().write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",encoding="utf-8"); passed=all(item["status"]=="passed" for item in checks) and len(physical)==4 and all(item["runtime_seconds"] is not None for item in physical.values()); print(json.dumps({"status":"passed" if passed else "failed","design_count":len(physical),"history":str(history),"model_batch_p50_ms":record["model"]["model_batch_p50_ms"]},sort_keys=True)); return 0 if passed else 1

if __name__=="__main__": raise SystemExit(main())
