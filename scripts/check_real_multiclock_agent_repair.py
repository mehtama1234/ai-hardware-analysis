"""Check the real OpenLane multi-clock CDC replay report."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument("report",type=Path);a=p.parse_args();r=json.loads(a.report.read_text());e=[];x={"schema_version":"real-openlane-multiclock-agent-repair-report-v1","repository":"OpenLane","baseline_status":"failed","agent_status":"available","patch_candidate_status":"review_required","repaired_status":"passed","canonical_unchanged":True,"status":"passed"}
    for k,v in x.items():
        if r.get(k)!=v:e.append(f"{k} mismatch")
    u=dict(r);q=u.pop("report_sha256",None)
    if q!=digest(u):e.append("digest mismatch")
    o={"schema_version":"real-openlane-multiclock-agent-repair-check-v1","status":"passed" if not e else "blocked","errors":e,"report":str(a.report)};o["check_sha256"]=digest(o);print(json.dumps(o,sort_keys=True));return 0 if not e else 1
if __name__=="__main__":raise SystemExit(main())
