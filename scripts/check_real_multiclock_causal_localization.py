"""Independently validate the real multi-clock causal report."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("report",type=Path); args=parser.parse_args(); report=json.loads(args.report.read_text()); expected=report.pop("report_sha256")
    actual=hashlib.sha256(json.dumps(report,sort_keys=True,separators=(",",":")).encode()).hexdigest(); frontier=report.get("frontier",{}); localization=report.get("localization",{})
    checks={"hash":expected==actual,"status":report.get("status")=="passed","canonical":report.get("canonical_status")=="passed","mutated":report.get("mutated_status")=="failed","frontier":frontier.get("status")=="diverged" and frontier.get("signal")=="maintenance_budget_core","binding":report.get("binding",{}).get("status")=="available","localization":localization.get("status")=="available","timeline":report.get("timeline",{}).get("status")=="available","integrity":report.get("integrity_errors")==[],"mutation_line":report.get("mutation_location",{}).get("line")==82}
    ok=all(checks.values()); print(json.dumps({"status":"passed" if ok else "failed","checks":checks},sort_keys=True)); return 0 if ok else 1
if __name__=="__main__": raise SystemExit(main())
