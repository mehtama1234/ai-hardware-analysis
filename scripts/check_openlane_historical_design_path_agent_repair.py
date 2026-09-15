"""Independently validate the OpenLane design-path replay."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument("report",type=Path); a=p.parse_args(); r=json.loads(a.report.read_text()); errors=[]; expected={"schema_version":"openlane-historical-design-path-agent-repair-report-v1","repository":"OpenLane","repository_revision":"ff5509f6","historical_source_revision":"41ed0036^","historical_fix_commit":"41ed0036","source_file":"scripts/utils/utils.py","baseline_status":"failed","agent_status":"available","patch_candidate_status":"review_required","repaired_status":"passed","canonical_unchanged":True,"status":"passed"}
 for k,v in expected.items():
  if r.get(k)!=v: errors.append(f"{k} expected {v!r}, got {r.get(k)!r}")
 u=dict(r); recorded=u.pop("report_sha256",None)
 if recorded!=digest(u): errors.append("report digest mismatch")
 out={"schema_version":"openlane-historical-design-path-agent-repair-check-v1","status":"passed" if not errors else "blocked","errors":errors,"report":str(a.report)}; out["check_sha256"]=digest(out); print(json.dumps(out,sort_keys=True)); return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
