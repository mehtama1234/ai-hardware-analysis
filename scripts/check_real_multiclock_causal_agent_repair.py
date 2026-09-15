"""Check causal evidence was consumed by the real CDC repair trajectory."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("report",type=Path); args=parser.parse_args(); report=json.loads(args.report.read_text()); expected=report.pop("report_sha256")
    causal=Path(report.get("causal_report", "")); frontier=report.get("causal_frontier", {})
    checks={"report_hash":expected==hashlib.sha256(json.dumps(report,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"repair_passed":report.get("status")=="passed","causal_file":causal.is_file(),"causal_digest":causal.is_file() and hashlib.sha256(causal.read_bytes()).hexdigest()==report.get("causal_report_sha256"),"frontier":frontier.get("status")=="diverged" and frontier.get("signal")=="maintenance_budget_core","agent_context":causal.is_file() and str(causal) in (report.get("causal_report") or "")}
    ok=all(checks.values()); print(json.dumps({"status":"passed" if ok else "failed","checks":checks},sort_keys=True)); return 0 if ok else 1
if __name__=="__main__": raise SystemExit(main())
