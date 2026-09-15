"""Independently check the error-budget causal-localization report."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
def main():
 p=argparse.ArgumentParser();p.add_argument("report",type=Path);a=p.parse_args();r=json.loads(a.report.read_text());expected=r.pop("report_sha256");actual=hashlib.sha256(json.dumps(r,sort_keys=True,separators=(",",":")).encode()).hexdigest();f=r.get("frontier",{});l=r.get("localization",{});checks={"hash":actual==expected,"status":r.get("status")=="passed","canonical":r.get("canonical_status")=="passed","mutated":r.get("mutated_status")=="passed","frontier":f.get("status")=="diverged" and f.get("signal")=="reason","binding":r.get("binding",{}).get("status")=="available","localization":l.get("status")=="available","timeline":r.get("timeline",{}).get("status")=="available","integrity":r.get("integrity_errors")==[],"mutation_line":r.get("mutation_location",{}).get("line")==50};ok=all(checks.values());print(json.dumps({"status":"passed" if ok else "failed","checks":checks},sort_keys=True));return 0 if ok else 1
if __name__=="__main__":raise SystemExit(main())
