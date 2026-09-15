"""Check the real OpenLane peripheral agent-repair report."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument("report",type=Path); a=p.parse_args(); r=json.loads(a.report.read_text()); e=[]; expected={"schema_version":"real-openlane-peripheral-agent-repair-report-v1","repository":"OpenLane","baseline_status":"failed","agent_status":"available","patch_candidate_status":"review_required","repaired_status":"passed","canonical_unchanged":True,"status":"passed"}
    for k,v in expected.items():
        if r.get(k)!=v:e.append(f"{k} mismatch")
    u=dict(r); q=u.pop("report_sha256",None)
    if q!=digest(u):e.append("digest mismatch")
    if r.get("causal_report"):
        causal=Path(r["causal_report"]);frontier=r.get("causal_frontier",{}) or {}
        if not causal.is_file() or hashlib.sha256(causal.read_bytes()).hexdigest()!=r.get("causal_report_sha256"):e.append("causal report digest mismatch")
        if frontier.get("status")!="diverged" or frontier.get("signal")!="control":e.append("causal frontier mismatch")
        if str(causal) not in r.get("causal_report",""):e.append("causal report not bound into context")
    out={"schema_version":"real-openlane-peripheral-agent-repair-check-v1","status":"passed" if not e else "blocked","errors":e,"report":str(a.report)};out["check_sha256"]=digest(out);print(json.dumps(out,sort_keys=True));return 0 if not e else 1
if __name__=="__main__": raise SystemExit(main())
