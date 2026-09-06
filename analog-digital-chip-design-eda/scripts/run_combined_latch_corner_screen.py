#!/usr/bin/env python3
"""Frozen seven-profile process/temperature diagnostic; not PVT signoff."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
PROFILES=[(corner,27) for corner in ("tt","ff","ss","fs","sf")]+[("tt",-40),("tt",125)]


def main():
    out=ROOT/"evidence/aimc-simulator-adapters/combined-latch-corner-screen"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False)
    contract={"profiles":PROFILES,"source_transient":"20260906T202600550851Z","combined_layout":"20260906T203539307640Z",
              "boundary":"Fixed nominal rails/bias/clocks, four alternating ±0.5 mV cycles; no supply sweep, parasitic corners, mismatch, noise or complete converter.",
              "runner_sha256":hashlib.sha256((ROOT/"scripts/run_latch_repeated_readout.py").read_bytes()).hexdigest()}
    (out/"contract.json").write_text(json.dumps(contract,indent=2)+"\n")
    rows=[]
    for corner,temperature in PROFILES:
        command=[sys.executable,str(ROOT/"scripts/run_latch_repeated_readout.py"),
                 str(ROOT/"evidence/aimc-simulator-adapters/isolated-latch-v2-transient/20260906T202600550851Z"),
                 "--reset-early-ns","0.5","--clock-fall-ps","1000","--reset-high-v","1.75","--combined-layout",
                 str(ROOT/"evidence/aimc-simulator-adapters/combined-latch-receiver/20260906T203539307640Z"),
                 "--corner",corner,"--temperature-c",str(temperature)]
        proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=90)
        (out/f"{corner}-{temperature}.log").write_text(proc.stdout+proc.stderr)
        lines=proc.stdout.strip().splitlines()
        run=Path(lines[-1]) if lines else None
        row={"corner":corner,"temperature_c":temperature,"returncode":proc.returncode,"measured":False}
        if run and run.is_relative_to(ROOT/"evidence/aimc-simulator-adapters/latch-repeated-readout") and (run/"result.json").exists():
            result=json.loads((run/"result.json").read_text())
            cycles=result.get("rows",[])
            row.update({"run":str(run),"status":result["status"],"measured":len(cycles)==4,
                        "logic_hold_reset_pass":len(cycles)==4 and all(r["sample_polarity_pass"] and r["hold_margin_pass"] and r["reset_pass"] and r["receiver_hold_pass"] for r in cycles),
                        "waveform_legal":result.get("waveform_legal",False),
                        "min_hold_diff_v":min((r["hold_min_signed_diff_v"] for r in cycles),default=None),
                        "result_sha256":hashlib.sha256((run/"result.json").read_bytes()).hexdigest()})
        rows.append(row)
        (out/"result.json").write_text(json.dumps({"status":"screen_complete_not_qualified" if len(rows)==len(PROFILES) else "screen_running",
                                                  "rows":rows,"accepted_converter":False},indent=2)+"\n")
        print(json.dumps(row),flush=True)
    print(out)


if __name__=="__main__":
    main()
