"""Localize a real OpenLane peripheral CSR mutation from a VCD trace."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];REPO=Path("/home/mehtama1/eda-tools/OpenLane")
DESIGN=Path("designs/peripheral/src");SOURCE=DESIGN/"csr_regs.sv";TOP=DESIGN/"peripheral.sv"
OLD="    else if (wr_en) control <= wdata; // SEEDED_BUG: decode addr zero before write";NEW="    else if (wr_en && addr == 2'd0) control <= wdata; // SEEDED_BUG: decode addr zero before write"
TB=r'''module tb;
reg clk=0,rst=1,valid=0,write=0; reg [1:0] addr=0; reg [7:0] wdata=0;
wire ready; wire [7:0] control;
peripheral dut(.*);
always #1 clk=~clk;
initial begin
  $dumpfile("trace.vcd"); $dumpvars(0,dut);
  #3 rst=0; valid=1; write=1; addr=2'd1; wdata=8'hA5;
  #4 valid=0; write=0; #3;
  if (control !== 8'h00) $display("FAIL csr_address_decode");
  else $display("PASS csr_address_decode");
  $finish;
end
endmodule
'''
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def held(path,signal,times,signal_values):
 samples=signal_values(path,signal);result=[];current=None;index=0
 for time in times:
  while index<len(samples) and samples[index][0]<=time:current=samples[index][1];index+=1
  if current is not None:result.append((time,current))
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 fixed=(REPO/SOURCE).read_text();assert fixed.count(NEW)==1
 with tempfile.TemporaryDirectory(prefix="real-peripheral-causal-") as td:
  t=Path(td);can=t/"canonical";mut=t/"mutated"
  for root in (can,mut):
   (root/DESIGN).mkdir(parents=True);(root/SOURCE).write_text(fixed);(root/TOP).write_text((REPO/TOP).read_text());(root/"tb.v").write_text(TB)
  (mut/SOURCE).write_text(fixed.replace(NEW,OLD));statuses=[]
  mutated_rtl_sha256=hashlib.sha256((mut/SOURCE).read_bytes()).hexdigest()
  persistent_source=a.output/"mutated_rtl"/SOURCE;persistent_source.parent.mkdir(parents=True,exist_ok=True);persistent_source.write_text((mut/SOURCE).read_text())
  for name,root in (("canonical",can),("mutated",mut)):
   out=a.output/name;out.mkdir(parents=True);b=out/"sim.vvp";c=subprocess.run(["iverilog","-g2012","-o",str(b),str(root/SOURCE),str(root/TOP),str(root/"tb.v")],capture_output=True,text=True);(out/"compile.stderr.log").write_text(c.stderr);v=subprocess.run(["vvp",str(b)],cwd=out,capture_output=True,text=True);(out/"simulation.stdout.log").write_text(v.stdout);statuses.append("passed" if c.returncode==0 and v.returncode==0 and (out/"trace.vcd").is_file() else "failed")
 import sys;sys.path.insert(0,str(ROOT/"analog-digital-chip-design-eda"))
 from verification_platform.waveform import signal_values
 from verification_platform.causal import bind_frontier_to_causal_graph,build_causal_graph,build_causal_timeline,rank_frontier_root_causes,state_frontier,trace_events,verify_causal_graph,verify_causal_timeline
 cw=a.output/"canonical"/"trace.vcd";mw=a.output/"mutated"/"trace.vcd";times=sorted({time for path in (cw,mw) for time,_ in signal_values(path,"control")});frontier=state_frontier(held(mw,"control",times,signal_values),held(cw,"control",times,signal_values),signal="control");source=str(persistent_source);events=trace_events(mw,["control","addr","valid","write","wdata"]);drivers={"control":{"addr","valid","write","wdata"},"addr":set(),"valid":set(),"write":set(),"wdata":set()};locations={("control","addr"): [{"file":source,"line":6}],("control","valid"): [{"file":source,"line":6}],("control","write"): [{"file":source,"line":6}],("control","wdata"): [{"file":source,"line":6}]};graph=build_causal_graph(events,drivers,driver_locations=locations);graph.update({"waveform":str(mw),"rtl":source,"signals":sorted(drivers),"rtl_sha256":mutated_rtl_sha256});graph["graph_sha256"]=sha({k:v for k,v in graph.items() if k!="graph_sha256"});binding=bind_frontier_to_causal_graph(frontier,graph);localization=rank_frontier_root_causes(binding,source);timeline=build_causal_timeline(graph,frontier_node=binding.get("frontier_node"));errors=verify_causal_graph(graph)+verify_causal_timeline(timeline,graph);report={"schema_version":"real-peripheral-causal-localization-report-v1","target":"OpenLane peripheral CSR hierarchy","canonical_status":statuses[0],"mutated_status":statuses[1],"frontier":frontier,"graph":graph,"binding":binding,"localization":localization,"timeline":timeline,"mutation_location":{"file":source,"line":6,"text":OLD},"integrity_errors":errors,"status":"passed" if statuses==["passed","passed"] and frontier.get("status")=="diverged" and binding.get("status")=="available" and localization.get("status")=="available" and timeline.get("status")=="available" and not errors else "blocked","claim_boundary":"real OpenLane two-module CSR first-divergence and source-bound causal localization; not proof of complete protocol root cause"};report["report_sha256"]=sha(report);path=a.output/"real-peripheral-causal-localization-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path),"frontier":frontier},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
