#!/usr/bin/env python3
"""Run formal properties for the repaired hierarchical register block."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RTL = ROOT / "benchmarks/register_peripheral"
PROPERTIES = RTL / "formal_properties.sv"
CASES = (("csr_reset_property", 4), ("csr_nonzero_address_property", 8), ("csr_zero_address_write_property", 8))

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--repaired-source", type=Path, required=True); parser.add_argument("--output", type=Path, required=True); args = parser.parse_args()
    source = args.repaired_source.resolve(); output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True); results=[]; logs=[]
    for top, sequence in CASES:
        command=["yosys", "-p", f"read_verilog -formal -sv {source} {PROPERTIES}; prep -top {top}; flatten; select -module {top}; sat -seq {sequence} -prove-asserts"]
        run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,check=False); log=run.stdout+run.stderr; logs.append(f"=== {top} ===\n{log}"); results.append({"property":top,"sequence":sequence,"returncode":run.returncode,"passed":run.returncode==0 and "SAT proof finished - no model found: SUCCESS!" in log})
    (output/"yosys.log").write_text("\n".join(logs),encoding="utf-8"); (output/"property-proofs.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
    passed=all(item["passed"] for item in results); report={"schema_version":"register-peripheral-formal-suite-v1","status":"passed" if passed else "failed","generated_at":datetime.now(timezone.utc).isoformat(),"source":{"path":str(source),"sha256":digest(source)},"specification":{"path":str(RTL/"spec.md"),"sha256":digest(RTL/"spec.md")},"proof":{"tool":"yosys-sat","property_count":len(results),"property_runs":results,"result":"proven" if passed else "unknown","log":str(output/"yosys.log")},"claim_boundary":"Local bounded formal properties for the CSR address/reset contract only; not full bus protocol, commercial signoff, or silicon evidence."}
    (output/"formal-report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8"); print(json.dumps({"status":report["status"],"property_count":len(results),"output":str(output)},sort_keys=True)); return 0 if passed else 1

if __name__ == "__main__": raise SystemExit(main())
