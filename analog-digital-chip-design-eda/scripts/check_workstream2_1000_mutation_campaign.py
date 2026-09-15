"""Independently check the Workstream 2 1,000-mutant campaign."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument("report",type=Path); a=p.parse_args(); r=json.loads(a.report.read_text()); e=[]
    expected={"campaign":"workstream2-10-design-1000-mutant-campaign","total_declared":1000,"total_mutations":1000,"design_count":10,"eligible_mutations":1000,"detected_mutations":1000,"false_pass_count":0,"blocked_count":0,"mutation_score":1.0,"status":"passed"}
    for k,v in expected.items():
        if r.get(k)!=v:e.append(f"{k} mismatch")
    ids=r.get("mutation_ids",[])
    if not isinstance(ids,list) or len(ids)!=1000 or len(set(ids))!=1000:e.append("mutation ids incomplete")
    records=sorted(a.report.parent.glob("*/mutation-result.json"))
    if len(records)!=1000:e.append(f"expected 1000 child records, found {len(records)}")
    for path in records:
        try:
            x=json.loads(path.read_text()); body={k:v for k,v in x.items() if k!="record_sha256"}; result=x.get("result",{}); rbody={k:v for k,v in result.items() if k!="result_sha256"}
            if x.get("record_sha256")!=digest(body) or result.get("result_sha256")!=digest(rbody):e.append(f"digest mismatch: {path}")
            for k in ("baseline_valid","detected","candidate_changed","canonical_unchanged"):
                if result.get(k) is not True:e.append(f"{k} failed: {path}")
            if result.get("false_pass") is not False:e.append(f"false pass: {path}")
        except Exception as ex:e.append(f"unreadable record {path}: {ex}")
    if r.get("report_sha256")!=digest({k:v for k,v in r.items() if k!="report_sha256"}):e.append("report digest mismatch")
    out={"schema_version":"workstream2-1000-mutation-check-v1","status":"passed" if not e else "blocked","errors":sorted(set(e)),"report":str(a.report)}; out["check_sha256"]=digest(out); print(json.dumps(out,sort_keys=True)); return 0 if not e else 1
if __name__=="__main__": raise SystemExit(main())
