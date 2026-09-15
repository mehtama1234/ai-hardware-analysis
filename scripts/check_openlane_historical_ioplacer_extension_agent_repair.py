"""Check the OpenLane I/O extension replay report."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument("report",type=Path); a=p.parse_args(); r=json.loads(a.report.read_text()); e=[]
    for k,v in {"schema_version":"openlane-historical-ioplacer-extension-agent-repair-report-v1","repository":"OpenLane","historical_fix_commit":"c98a290f7046bed7ef7c37d1f06927c0b6071e67","baseline_status":"failed","agent_status":"available","patch_candidate_status":"review_required","repaired_status":"passed","canonical_unchanged":True,"status":"passed"}.items():
        if r.get(k)!=v:e.append(f"{k} mismatch")
    u=dict(r); q=u.pop("report_sha256",None)
    if q!=digest(u):e.append("digest mismatch")
    out={"schema_version":"openlane-historical-ioplacer-extension-agent-repair-check-v1","status":"passed" if not e else "blocked","errors":e,"report":str(a.report)}; out["check_sha256"]=digest(out); print(json.dumps(out,sort_keys=True)); return 0 if not e else 1
if __name__=="__main__": raise SystemExit(main())
