#!/usr/bin/env python3
"""Run temporal properties against the actual AIMC multi-clock subsystem."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RTL=ROOT/"labs/digital/aimc-control-plane-rtl"
SOURCES=[RTL/name for name in ("aimc_multi_clock_control_subsystem.v", "aimc_micro_tile_controller.v", "aimc_operation_partition.v", "aimc_tile_readout.v", "aimc_scheduler_governor.v", "aimc_tile_service_scheduler.v", "aimc_error_budget_governor.v")]
TB=RTL/"aimc_sequential_properties_tb.v"

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--output",type=Path,required=True); args=parser.parse_args(); output=args.output.resolve(); output.mkdir(parents=True,exist_ok=True)
    binary=output/"aimc_sequential_properties.vvp"; compile_run=subprocess.run(["iverilog","-g2012","-o",str(binary),*map(str,SOURCES),str(TB)],cwd=ROOT,capture_output=True,text=True,check=False); sim_run=subprocess.run(["vvp",str(binary)],cwd=ROOT,capture_output=True,text=True,check=False) if compile_run.returncode==0 else None
    (output/"compile.stdout.log").write_text(compile_run.stdout,encoding="utf-8"); (output/"compile.stderr.log").write_text(compile_run.stderr,encoding="utf-8"); stdout=sim_run.stdout if sim_run else ""; stderr=sim_run.stderr if sim_run else ""; (output/"simulation.stdout.log").write_text(stdout,encoding="utf-8"); (output/"simulation.stderr.log").write_text(stderr,encoding="utf-8")
    names=["reset_determinism","cdc_not_visible_after_one_core_edge","cdc_visible_after_two_core_edges","registered_nominal_acceptance","disabled_tile_fallback_accounting","cdc_second_transition_hidden_one_edge","cdc_second_transition_visible_two_edges","cdc_third_transition_hidden_one_edge","cdc_third_transition_visible_two_edges","repeated_acceptance_accounting","repeated_fallback_accounting","acceptance_fallback_partition","reset_recovery_clears_accounting","reset_recovery_starts_clean"]; results=[{"property":name,"passed":f"PASS property={name}" in stdout} for name in names]; passed=compile_run.returncode==0 and sim_run is not None and sim_run.returncode==0 and all(item["passed"] for item in results) and "PASS aimc_sequential_properties_tb" in stdout
    report={"schema_version":"aimc-sequential-property-suite-v1","status":"passed" if passed else "failed","generated_at":datetime.now(timezone.utc).isoformat(),"scope":"Actual AIMC multi-clock subsystem temporal simulation: reset, repeated two-edge CDC latency in both directions, registered acceptance/fallback accounting, partition invariants, and reset recovery.","sources":[{"path":str(path),"sha256":digest(path)} for path in [*SOURCES,TB]],"proof":{"tool":"iverilog-vvp","property_count":len(results),"property_runs":results,"compile_returncode":compile_run.returncode,"simulation_returncode":sim_run.returncode if sim_run else None,"result":"passed" if passed else "unknown","stdout":str(output/"simulation.stdout.log")},"claim_boundary":"Simulation-backed temporal stress evidence only; not exhaustive formal CDC proof, commercial signoff, analog measurement, or silicon evidence."}
    (output/"sequential-report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8"); print(json.dumps({"status":report["status"],"property_count":len(results),"output":str(output)},sort_keys=True)); return 0 if passed else 1

if __name__=="__main__": raise SystemExit(main())
