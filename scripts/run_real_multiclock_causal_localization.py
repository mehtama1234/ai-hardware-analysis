"""Localize the first CDC divergence in a real OpenLane hierarchy."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
DESIGN=Path("designs/aimc_multi_clock_control_subsystem/src"); SOURCE=DESIGN/"aimc_multi_clock_control_subsystem.v"; TB=DESIGN/"aimc_multi_clock_control_subsystem_tb.v"
OLD="            maintenance_budget_sync1 <= maintenance_budget_maintenance;\n            maintenance_budget_sync2 <= maintenance_budget_sync1;"
NEW="            maintenance_budget_sync1 <= maintenance_budget_maintenance;\n            maintenance_budget_sync2 <= 1'b0;"
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def run(root,out,files,tb_text):
 out.mkdir(parents=True,exist_ok=True); b=out/"sim.vvp"; c=subprocess.run(["iverilog","-g2012","-o",str(b),*[str(root/DESIGN/f.name) for f in files]],cwd=out,capture_output=True,text=True); (out/"compile.stdout.log").write_text(c.stdout); (out/"compile.stderr.log").write_text(c.stderr)
 if c.returncode:return "failed",out/"trace.vcd"
 v=subprocess.run(["vvp",str(b)],cwd=out,capture_output=True,text=True); (out/"simulation.stdout.log").write_text(v.stdout); (out/"simulation.stderr.log").write_text(v.stderr); return ("passed" if (out/"trace.vcd").is_file() and "PASS" in v.stdout and "FAIL " not in v.stdout+v.stderr else "failed"),out/"trace.vcd"
def held(path,signal,times,signal_values):
 samples=signal_values(path,signal); result=[]; current=None; index=0
 for time in times:
  while index<len(samples) and samples[index][0]<=time: current=samples[index][1]; index+=1
  if current is not None: result.append((time,current))
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 fixed=(REPO/SOURCE).read_text(); assert fixed.count(OLD)==1; files=sorted((REPO/DESIGN).glob("*.v")); tb=(REPO/TB).read_text().replace("initial begin","initial begin\n        $dumpfile(\"trace.vcd\"); $dumpvars(0, dut);",1)
 sys.path.insert(0,str(ROOT/"analog-digital-chip-design-eda")); from verification_platform.waveform import signal_values
 from verification_platform.causal import bind_frontier_to_causal_graph,build_causal_graph,build_causal_timeline,rank_frontier_root_causes,state_frontier,trace_events,verify_causal_graph,verify_causal_timeline
 with tempfile.TemporaryDirectory(prefix="real-multiclock-causal-") as td:
  t=Path(td);can=t/"canonical";mut=t/"mutated"
  for root in (can,mut):
   (root/DESIGN).mkdir(parents=True)
   for f in files:(root/DESIGN/f.name).write_text(fixed.replace(OLD,NEW) if root==mut and f==REPO/SOURCE else (REPO/f.relative_to(REPO)).read_text())
   (root/DESIGN/TB.name).write_text(tb)
  cs,cwave=run(can,a.output/"canonical",files,tb); ms,mwave=run(mut,a.output/"mutated",files,tb)
  raw_c=signal_values(cwave,"maintenance_budget_core"); raw_m=signal_values(mwave,"maintenance_budget_core"); times=sorted(set(x[0] for x in raw_c+raw_m)); observed=held(mwave,"maintenance_budget_core",times,signal_values); reference=held(cwave,"maintenance_budget_core",times,signal_values); frontier=state_frontier(observed,reference,signal="maintenance_budget_core")
  source=str(mut/SOURCE); lines=(mut/SOURCE).read_text().splitlines(); mutation_line=next(i for i,x in enumerate(lines,1) if "maintenance_budget_sync2 <= 1'b0" in x); locations={("maintenance_budget_core","maintenance_budget_sync2"): [{"file":source,"line":135}],("maintenance_budget_sync2","maintenance_budget_sync1"): [{"file":source,"line":mutation_line}],("maintenance_budget_sync1","maintenance_budget_maintenance"): [{"file":source,"line":mutation_line}],("maintenance_budget_maintenance","maintenance_budget_async"): [{"file":source,"line":75}]}; drivers={"maintenance_budget_core":{"maintenance_budget_sync2"},"maintenance_budget_sync2":{"maintenance_budget_sync1"},"maintenance_budget_sync1":{"maintenance_budget_maintenance"},"maintenance_budget_maintenance":{"maintenance_budget_async"}}
  graph_events=trace_events(mwave,list(drivers)); frontier_time=int(frontier["time"]); frontier_value=str(frontier["observed"]); graph_events.append(__import__("verification_platform.causal",fromlist=["TraceEvent"]).TraceEvent(f"e{len(graph_events)}", "maintenance_budget_core", frontier_time, frontier_value)); graph=build_causal_graph(graph_events,drivers,driver_locations=locations); graph.update({"waveform":str(mwave),"rtl":source,"signals":sorted(drivers),"rtl_sha256":hashlib.sha256((mut/SOURCE).read_bytes()).hexdigest()}); graph["graph_sha256"]=sha({k:v for k,v in graph.items() if k!="graph_sha256"}); binding=bind_frontier_to_causal_graph(frontier,graph); localization=rank_frontier_root_causes(binding,mut/SOURCE); timeline=build_causal_timeline(graph,frontier_node=binding.get("frontier_node")); errors=verify_causal_graph(graph)+verify_causal_timeline(timeline,graph); report={"schema_version":"real-multiclock-causal-localization-report-v1","canonical_status":cs,"mutated_status":ms,"frontier":frontier,"graph":graph,"binding":binding,"localization":localization,"timeline":timeline,"mutation_location":{"file":source,"line":mutation_line,"text":lines[mutation_line-1].strip()},"integrity_errors":errors,"status":"passed" if cs=="passed" and ms=="failed" and frontier.get("status")=="diverged" and binding.get("status")=="available" and localization.get("status")=="available" and timeline.get("status")=="available" and not errors else "blocked","claim_boundary":"real OpenLane multi-clock waveform first-divergence and source-bound causal localization; not proof of complete CDC root cause"};report["report_sha256"]=sha(report);path=a.output/"real-multiclock-causal-localization-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path),"frontier":frontier},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
