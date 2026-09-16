#!/usr/bin/env python3
"""Independently check the flagship definition-of-done audit."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("audit",type=Path);a=p.parse_args();ap=a.audit.resolve();errors=[]
 try:x=json.loads(ap.read_text())
 except (OSError,json.JSONDecodeError) as e:print(json.dumps({"status":"blocked","errors":[str(e)]}));return 1
 if x.get("schema_version")!="flagship-definition-of-done-audit-v1" or x.get("audit_sha256")!=digest({k:v for k,v in x.items() if k!="audit_sha256"}):errors.append("audit schema or digest mismatch")
 if x.get("completion") is not False or x.get("status")!="blocked_pending_requirements" or set(x.get("blocking_requirements",[])) not in ({4,7},{7}):errors.append("audit does not preserve required incomplete gates")
 req={r.get("id"):r for r in x.get("requirements",[])}
 if set(req)!=set(range(1,13)):errors.append("requirement audit is incomplete")
 if req.get(4,{}).get("status") not in {"pending","passed"} or req.get(7,{}).get("status")!="blocked":errors.append("human/generalization statuses are unsafe")
 if x.get("release_decision")!="blocked_pending_physical_and_measured_gates":errors.append("release decision is not fail-closed")
 for name,item in x.get("evidence",{}).items():
  path=ap.parent.parent/item.get("path","")
  if not path.is_file() or (item.get("sha256") and hashlib.sha256(path.read_bytes()).hexdigest()!=item.get("sha256")):errors.append(f"evidence digest mismatch: {name}")
 if "not human approval" not in x.get("claim_boundary","").lower() or "production release" not in x.get("claim_boundary","").lower():errors.append("audit claim boundary is too broad")
 result={"schema_version":"flagship-definition-of-done-audit-check-v1","status":"passed" if not errors else "blocked","audit":str(ap),"blocking_requirements":x.get("blocking_requirements"),"errors":sorted(set(errors))};result["check_sha256"]=digest(result);print(json.dumps(result,sort_keys=True));return 0 if not errors else 1
if __name__=="__main__":raise SystemExit(main())
