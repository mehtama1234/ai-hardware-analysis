"""Independently check the real multi-module RTL catalog."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument("report",type=Path); a=p.parse_args(); r=json.loads(a.report.read_text()); e=[]
    if r.get("schema_version")!="real-multimodule-rtl-catalog-v1" or r.get("status")!="passed":e.append("catalog status/schema invalid")
    designs=r.get("designs",[])
    if r.get("target_count")!=10 or len(designs)!=10:e.append("expected exactly ten targets")
    if len({(x.get("repository"),x.get("root")) for x in designs})!=10:e.append("targets are not distinct")
    for d in designs:
        if d.get("rtl_file_count",0)<2 or d.get("compile_status")!="passed":e.append(f"target not compiled: {d.get('root')}")
        for item in d.get("rtl_files",[]):
            path=Path(item.get("path",""))
            if not path.is_file():e.append(f"missing RTL: {path}")
            elif hashlib.sha256(path.read_bytes()).hexdigest()!=item.get("sha256"):e.append(f"RTL digest mismatch: {path}")
    if r.get("report_sha256")!=digest({k:v for k,v in r.items() if k!="report_sha256"}):e.append("report digest mismatch")
    out={"schema_version":"real-multimodule-rtl-catalog-check-v1","status":"passed" if not e else "blocked","errors":sorted(set(e)),"report":str(a.report)};out["check_sha256"]=digest(out);print(json.dumps(out,sort_keys=True));return 0 if not e else 1
if __name__=="__main__": raise SystemExit(main())
