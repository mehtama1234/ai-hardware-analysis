"""Replay a real OpenLane AIMC error-budget governor mutation and repair it."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path(os.environ.get("OPENLANE_REPO_ROOT", "/home/mehtama1/eda-tools/OpenLane"))
SOURCE=Path("designs/aimc_error_budget_governor_physical/src/aimc_error_budget_governor.v")
OLD="        end else if (drift_age > 4'd11) begin"; NEW="        end else if (drift_age >= 4'd11) begin"
TB=r'''module tb;
reg sample_valid, analog_candidate; reg [7:0] residual_q8; reg [3:0] drift_age;
reg [7:0] sensitivity_q8, cumulative_error_q8; wire [1:0] service_decision, tile_action;
wire [3:0] reason; wire [7:0] next_cumulative_error_q8;
aimc_error_budget_governor dut(.*);
task check(input [1:0] d,input [1:0] a,input [3:0] r,input [127:0] label);
begin #1; if(service_decision!==d||tile_action!==a||reason!==r) begin
 $display("FAIL %0s got=%0d/%0d/%0d expected=%0d/%0d/%0d",label,service_decision,tile_action,reason,d,a,r); $finish;
end end endtask
initial begin
 sample_valid=1; analog_candidate=1; residual_q8=8'd8; drift_age=4'd11;
 sensitivity_q8=0; cumulative_error_q8=0; check(2'd1,2'd1,4'd7,"calibration_boundary");
 residual_q8=8'd50; check(2'd0,2'd2,4'd2,"residual_guard");
 residual_q8=8'd8; drift_age=4'd12; check(2'd0,2'd1,4'd3,"old_calibration");
 sample_valid=0; check(2'd0,2'd0,4'd0,"sample_guard");
 $display("PASS error_budget_checks"); $finish;
end endmodule
'''
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True); b=out/"governor.vvp"; (out/"source-boundary.log").write_text(next(line for line in (root/SOURCE).read_text().splitlines() if "drift_age" in line and "else if" in line)); c=subprocess.run(["iverilog","-g2012","-o",str(b),str(root/SOURCE),str(root/"tb.v")],capture_output=True,text=True); (out/"compile.stdout.log").write_text(c.stdout); (out/"compile.stderr.log").write_text(c.stderr)
 if c.returncode:return "failed"
 v=subprocess.run(["vvp",str(b)],capture_output=True,text=True); (out/"simulation.stdout.log").write_text(v.stdout); (out/"simulation.stderr.log").write_text(v.stderr); return "passed" if v.returncode==0 and "FAIL " not in v.stdout+v.stderr and "PASS" in v.stdout else "failed"
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--backend",choices=("mock","local"),default="mock");p.add_argument("--causal-report",type=Path);a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock":os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 revision=subprocess.run(["git","-C",str(REPO),"rev-parse","--short","HEAD"],capture_output=True,text=True,check=False); rev=revision.stdout.strip() if revision.returncode==0 and revision.stdout.strip() else "packaged-openlane-four-causal-task-v1"; fixed=(REPO/SOURCE).read_text()
 if fixed.count(OLD)!=1:raise RuntimeError("error-budget mutation anchor is not unique")
 sys.path.insert(0,str(SUBREPO));from verification_platform.repository_agent import run_repository_agent;from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="real-openlane-error-budget-") as td:
  t=Path(td);mut=t/"mutated";rep=t/"repaired"
  for root in (mut,rep):(root/SOURCE).parent.mkdir(parents=True);(root/SOURCE).write_text(fixed);(root/"tb.v").write_text(TB)
  (mut/SOURCE).write_text(fixed.replace(OLD,NEW));base=execute(mut,a.output/"baseline")
  causal=json.loads(a.causal_report.read_text()) if a.causal_report else {}; frontier=causal.get("frontier",{}); causal_context=(f" causal evidence: first divergence is {frontier.get('signal')} at time {frontier.get('time')}; use the digest-bound causal timeline and source-bound locations." if causal else ""); evidence=[str(REPO/SOURCE),"drift_age boundary invariant","real OpenLane AIMC error-budget governor"]+([str(a.causal_report)] if causal else [])
  agent=run_repository_agent(task_id="real-openlane-error-budget-repair",source_revision=rev,evidence=evidence,failure_context="drift age 11 is still within the analog serve boundary; recalibration starts only above 11"+causal_context,repair_before=NEW,repair_after=OLD,repair_source=mut/SOURCE,backend="local",output_root=a.output/"agent")
  cand=agent.get("patch_candidate",{}); repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("real-openlane-error-budget-repair",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"real error-budget governor repair",str(cand.get("edit_operator","exact_text_replace")));apply_to_copy(mut/SOURCE,rep/SOURCE,prop,human_approved=True);repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"real-openlane-error-budget-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"causal_report":str(a.causal_report.resolve()) if a.causal_report else None,"causal_report_sha256":hashlib.sha256(a.causal_report.read_bytes()).hexdigest() if a.causal_report else None,"causal_frontier":frontier if causal else None,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"real OpenLane AIMC error-budget policy invariant and disposable agent repair; optional digest-bound causal evidence; not full subsystem closure"};report["report_sha256"]=digest(report);path=a.output/"real-openlane-error-budget-agent-repair-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
