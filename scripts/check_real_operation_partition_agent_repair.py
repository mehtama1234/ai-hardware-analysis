"""Independent checker for the real operation-partition replay certificate."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("report", type=Path); a=p.parse_args(); r=json.loads(a.report.read_text()); expected=r.pop("report_sha256"); actual=hashlib.sha256(json.dumps(r,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    causal=Path(r.get("causal_report", "")) if r.get("causal_report") else None
    frontier=r.get("causal_frontier", {}) or {}
    checks={"hash":actual==expected,"status":r.get("status")=="passed","baseline":r.get("baseline_status")=="failed","agent":r.get("agent_status")=="available","candidate":r.get("patch_candidate_status")=="review_required","repaired":r.get("repaired_status")=="passed","canonical":r.get("canonical_unchanged") is True}
    if causal:
        checks.update({"causal_file":causal.is_file(),"causal_digest":causal.is_file() and hashlib.sha256(causal.read_bytes()).hexdigest()==r.get("causal_report_sha256"),"frontier":frontier.get("status")=="diverged" and frontier.get("signal")=="reason","agent_context":str(causal) in (r.get("causal_report") or "")})
    ok=all(checks.values()); print(json.dumps({"status":"passed" if ok else "failed","checks":checks},sort_keys=True)); return 0 if ok else 1
if __name__ == "__main__": raise SystemExit(main())
