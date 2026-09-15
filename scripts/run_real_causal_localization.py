"""Run causal localization on a real OpenLane AIMC mutation."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
SOURCE=Path("designs/aimc_operation_partition_physical/src/aimc_operation_partition.v")
OLD="    wire stale_weak_tiles = (calibration_age >= 16'd1024) && (weak_tiles >= 8'd4);"
NEW="    wire stale_weak_tiles = (calibration_age > 16'd1024) && (weak_tiles >= 8'd4);"
TB=r'''module tb;
reg sample_valid, analog_candidate; reg [3:0] op_class; reg resident_weights; reg [7:0] estimated_state_error;
reg [7:0] state_error_budget, attention_flip_rate, attention_flip_budget;
reg [7:0] token_flip_rate, token_flip_budget; reg [15:0] calibration_age; reg [7:0] weak_tiles;
wire [1:0] placement; wire [3:0] observed_reason;
aimc_operation_partition dut(.op_class(op_class),.resident_weights(resident_weights),.estimated_state_error(estimated_state_error),.state_error_budget(state_error_budget),.attention_flip_rate(attention_flip_rate),.attention_flip_budget(attention_flip_budget),.token_flip_rate(token_flip_rate),.token_flip_budget(token_flip_budget),.calibration_age(calibration_age),.weak_tiles(weak_tiles),.placement(placement),.reason(observed_reason));
initial begin
  op_class=4'd4; resident_weights=1; estimated_state_error=0; state_error_budget=4;
  attention_flip_rate=0; attention_flip_budget=2; token_flip_rate=0; token_flip_budget=2;
  sample_valid=0; analog_candidate=0; calibration_age=0; weak_tiles=0;
  $dumpfile("trace.vcd"); $dumpvars(0,dut);
  #5 op_class=4'd2; calibration_age=16'd1024; weak_tiles=8'd4;
  #5 $finish;
end
endmodule
'''
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def run(root,out):
 out.mkdir(parents=True,exist_ok=True); b=out/"sim.vvp"; c=subprocess.run(["iverilog","-g2012","-o",str(b),str(root/SOURCE),str(root/"tb.v")],cwd=out,capture_output=True,text=True); (out/"compile.stdout.log").write_text(c.stdout); (out/"compile.stderr.log").write_text(c.stderr)
 if c.returncode:return "failed",out/"trace.vcd"
 v=subprocess.run(["vvp",str(b)],cwd=out,capture_output=True,text=True); (out/"simulation.stdout.log").write_text(v.stdout); (out/"simulation.stderr.log").write_text(v.stderr); return ("passed" if v.returncode==0 and (out/"trace.vcd").is_file() else "failed"),out/"trace.vcd"
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 fixed=(REPO/SOURCE).read_text(); assert fixed.count(OLD)==1
 sys.path.insert(0,str(ROOT/"analog-digital-chip-design-eda")); from verification_platform.waveform import signal_values
 from verification_platform.causal import TraceEvent,bind_frontier_to_causal_graph,build_causal_graph,build_causal_timeline,rank_frontier_root_causes,state_frontier,trace_events,verify_causal_graph,verify_causal_timeline
 with tempfile.TemporaryDirectory(prefix="real-causal-localization-") as td:
  t=Path(td);can=t/"canonical";mut=t/"mutated"
  for root in (can,mut):(root/SOURCE).parent.mkdir(parents=True);(root/SOURCE).write_text(fixed);(root/"tb.v").write_text(TB)
  (mut/SOURCE).write_text(fixed.replace(OLD,NEW)); cs,cwave=run(can,a.output/"canonical"); ms,mwave=run(mut,a.output/"mutated")
  observed=signal_values(mwave,"reason"); reference=signal_values(cwave,"reason"); frontier=state_frontier(observed,reference,signal="reason")
  source=str(mut/SOURCE); line=next(i for i,x in enumerate((mut/SOURCE).read_text().splitlines(),1) if "wire stale_weak_tiles" in x)
  events=trace_events(mwave,["reason","stale_weak_tiles","calibration_age","weak_tiles"])
  graph=build_causal_graph(events,{"reason":{"stale_weak_tiles"},"stale_weak_tiles":{"calibration_age","weak_tiles"}},driver_locations={("reason","stale_weak_tiles"): [{"file":source,"line":63}],("stale_weak_tiles","calibration_age"):[{"file":source,"line":line}],("stale_weak_tiles","weak_tiles"):[{"file":source,"line":line}]})
  graph["waveform"]=str(mwave);graph["rtl"]=source;graph["signals"]=["reason","stale_weak_tiles","calibration_age","weak_tiles"];graph["rtl_sha256"]=hashlib.sha256((mut/SOURCE).read_bytes()).hexdigest();body={k:v for k,v in graph.items() if k!="graph_sha256"};graph["graph_sha256"]=sha(body)
  binding=bind_frontier_to_causal_graph(frontier,graph); localization=rank_frontier_root_causes(binding,mut/SOURCE); timeline=build_causal_timeline(graph,frontier_node=binding.get("frontier_node")); errors=verify_causal_graph(graph)+verify_causal_timeline(timeline,graph)
  report={"schema_version":"real-causal-localization-report-v1","target":"OpenLane AIMC operation partition","canonical_status":cs,"mutated_status":ms,"frontier":frontier,"graph":graph,"binding":binding,"localization":localization,"timeline":timeline,"mutation_location":{"file":source,"line":line,"text":(mut/SOURCE).read_text().splitlines()[line-1].strip()},"integrity_errors":errors,"status":"passed" if cs=="passed" and ms=="passed" and frontier.get("status")=="diverged" and binding.get("status")=="available" and localization.get("status")=="available" and timeline.get("status")=="available" and not errors else "blocked","claim_boundary":"deterministic real-waveform first-divergence and source-bound causal localization; not proof that the ranked statement is the complete root cause"};report["report_sha256"]=sha(report);path=a.output/"real-causal-localization-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path),"frontier":frontier,"candidates":localization.get("candidates",[])},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
