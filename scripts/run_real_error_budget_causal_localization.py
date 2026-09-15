"""Localize a real OpenLane AIMC error-budget boundary mutation."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
SOURCE=Path("designs/aimc_error_budget_governor_physical/src/aimc_error_budget_governor.v")
OLD="        end else if (drift_age > 4'd11) begin"; NEW="        end else if (drift_age >= 4'd11) begin"
TB=r'''module tb;
reg sample_valid, analog_candidate; reg [7:0] residual_q8; reg [3:0] drift_age;
reg [7:0] sensitivity_q8, cumulative_error_q8; wire [1:0] service_decision, tile_action;
wire [3:0] reason; wire [7:0] next_cumulative_error_q8;
aimc_error_budget_governor dut(.*);
initial begin
  sample_valid=1; analog_candidate=1; residual_q8=8'd8; drift_age=4'd11;
  sensitivity_q8=0; cumulative_error_q8=0;
  $dumpfile("trace.vcd"); $dumpvars(0,dut); #1;
  if (service_decision !== 2'd1 || tile_action !== 2'd1 || reason !== 4'd7) $display("FAIL boundary");
  else $display("PASS boundary");
  $finish;
end
endmodule
'''
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":" )).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 fixed=(REPO/SOURCE).read_text(); assert fixed.count(OLD)==1
 with tempfile.TemporaryDirectory(prefix="real-error-budget-causal-") as td:
  t=Path(td); can=t/"canonical"; mut=t/"mutated"
  for root in (can,mut): (root/SOURCE).parent.mkdir(parents=True);(root/SOURCE).write_text(fixed);(root/"tb.v").write_text(TB)
  (mut/SOURCE).write_text(fixed.replace(OLD,NEW))
  statuses=[]
  for name,root in (("canonical",can),("mutated",mut)):
   out=a.output/name;out.mkdir(parents=True);b=out/"sim.vvp";c=subprocess.run(["iverilog","-g2012","-o",str(b),str(root/SOURCE),str(root/"tb.v")],capture_output=True,text=True);(out/"compile.stderr.log").write_text(c.stderr)
   v=subprocess.run(["vvp",str(b)],cwd=out,capture_output=True,text=True);(out/"simulation.stdout.log").write_text(v.stdout);statuses.append("passed" if c.returncode==0 and v.returncode==0 and (out/"trace.vcd").is_file() else "failed")
  sys_path=str(ROOT/"analog-digital-chip-design-eda"); import sys;sys.path.insert(0,sys_path)
  from verification_platform.waveform import signal_values
  from verification_platform.causal import TraceEvent,bind_frontier_to_causal_graph,build_causal_graph,build_causal_timeline,rank_frontier_root_causes,state_frontier,trace_events,verify_causal_graph,verify_causal_timeline
  cw=a.output/"canonical"/"trace.vcd";mw=a.output/"mutated"/"trace.vcd";observed=signal_values(mw,"reason");reference=signal_values(cw,"reason");frontier=state_frontier(observed,reference,signal="reason")
  source=str(mut/SOURCE);events=trace_events(mw,["reason","drift_age"]);graph=build_causal_graph(events,{"reason":{"drift_age"},"drift_age":set()},driver_locations={("reason","drift_age"): [{"file":source,"line":50}]});graph.update({"waveform":str(mw),"rtl":source,"signals":["reason","drift_age"],"rtl_sha256":hashlib.sha256((mut/SOURCE).read_bytes()).hexdigest()});graph["graph_sha256"]=sha({k:v for k,v in graph.items() if k!="graph_sha256"});binding=bind_frontier_to_causal_graph(frontier,graph);localization=rank_frontier_root_causes(binding,mut/SOURCE);timeline=build_causal_timeline(graph,frontier_node=binding.get("frontier_node"));errors=verify_causal_graph(graph)+verify_causal_timeline(timeline,graph)
  report={"schema_version":"real-error-budget-causal-localization-report-v1","target":"OpenLane AIMC error-budget governor","canonical_status":statuses[0],"mutated_status":statuses[1],"frontier":frontier,"graph":graph,"binding":binding,"localization":localization,"timeline":timeline,"mutation_location":{"file":source,"line":50,"text":(mut/SOURCE).read_text().splitlines()[49].strip()},"integrity_errors":errors,"status":"passed" if statuses==["passed","passed"] and frontier.get("status")=="diverged" and binding.get("status")=="available" and localization.get("status")=="available" and timeline.get("status")=="available" and not errors else "blocked","claim_boundary":"real OpenLane combinational policy first-divergence and source-bound causal localization; not proof of complete root cause"};report["report_sha256"]=sha(report);path=a.output/"real-error-budget-causal-localization-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path),"frontier":frontier},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
