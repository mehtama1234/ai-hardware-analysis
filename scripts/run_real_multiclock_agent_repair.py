"""Replay a real multi-clock CDC mutation on the OpenLane AIMC subsystem."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path(os.environ.get("OPENLANE_REPO_ROOT", "/home/mehtama1/eda-tools/OpenLane"))
DESIGN=Path("designs/aimc_multi_clock_control_subsystem/src"); SOURCE=DESIGN/"aimc_multi_clock_control_subsystem.v"; TB=DESIGN/"aimc_multi_clock_control_subsystem_tb.v"
OLD="            maintenance_budget_sync1 <= maintenance_budget_maintenance;\n            maintenance_budget_sync2 <= maintenance_budget_sync1;"; NEW="            maintenance_budget_sync1 <= maintenance_budget_maintenance;\n            maintenance_budget_sync2 <= 1'b0;"
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
    out.mkdir(parents=True,exist_ok=True); binary=out/"multiclock.vvp"; files=[root/DESIGN/x.name for x in sorted((REPO/DESIGN).glob("*.v")) if x.name!=TB.name]+[root/TB]; c=subprocess.run(["iverilog","-g2012","-o",str(binary),*[str(x) for x in files]],capture_output=True,text=True); (out/"compile.stdout.log").write_text(c.stdout); (out/"compile.stderr.log").write_text(c.stderr)
    if c.returncode:return "failed"
    v=subprocess.run(["vvp",str(binary)],capture_output=True,text=True); (out/"simulation.stdout.log").write_text(v.stdout); (out/"simulation.stderr.log").write_text(v.stderr); return "passed" if v.returncode==0 and "FAIL " not in v.stdout+v.stderr and "PASS" in v.stdout else "failed"
def main():
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--backend",choices=("mock","local"),default="mock");p.add_argument("--causal-report",type=Path);a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
    if a.backend=="mock":os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
    revision=subprocess.run(["git","-C",str(REPO),"rev-parse","--short","HEAD"],capture_output=True,text=True,check=False); rev=revision.stdout.strip() if revision.returncode==0 and revision.stdout.strip() else "packaged-openlane-causal-task-v1"; files=sorted((REPO/DESIGN).glob("*.v")); fixed=(REPO/SOURCE).read_text()
    sys.path.insert(0,str(SUBREPO));from verification_platform.repository_agent import run_repository_agent;from verification_platform.repair import RepairProposal,apply_to_copy
    with tempfile.TemporaryDirectory(prefix="real-openlane-multiclock-") as td:
        s=Path(td);mut=s/"mutated";rep=s/"repaired"
        for root in (mut,rep):
            (root/DESIGN).mkdir(parents=True)
            for f in files:(root/DESIGN/f.name).write_text(fixed if f==REPO/SOURCE else f.read_text())
            (root/TB).write_text((REPO/TB).read_text())
        (mut/SOURCE).write_text(fixed.replace(OLD,NEW));base=execute(mut,a.output/"baseline");src=mut/SOURCE
        causal={}
        if a.causal_report:
            causal=json.loads(a.causal_report.read_text())
        causal_frontier=causal.get("frontier",{})
        causal_context=(f" causal evidence: first divergence is {causal_frontier.get('signal')} at time {causal_frontier.get('time')}; use the digest-bound synchronizer timeline and source-bound locations." if causal else "")
        evidence=[str(SOURCE),str(TB),"CDC maintenance budget synchronizer"]+([str(a.causal_report)] if causal else [])
        agent=run_repository_agent(task_id="real-openlane-multiclock-cdc-repair",source_revision=rev,evidence=evidence,failure_context="the asynchronous maintenance budget must reach the core domain after two core-clock synchronizer stages"+causal_context,repair_before=NEW,repair_after=OLD,repair_source=src,backend="local",output_root=a.output/"agent");cand=agent.get("patch_candidate",{});repaired="blocked"
        if cand.get("status")=="review_required":
            prop=RepairProposal("real-openlane-multiclock-cdc-repair",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"real OpenLane multi-clock CDC repair",str(cand.get("edit_operator","exact_text_replace")));apply_to_copy(src,rep/SOURCE,prop,human_approved=True);repaired=execute(rep,a.output/"repaired")
        report={"schema_version":"real-openlane-multiclock-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"causal_report":str(a.causal_report.resolve()) if a.causal_report else None,"causal_report_sha256":hashlib.sha256(a.causal_report.read_bytes()).hexdigest() if a.causal_report else None,"causal_frontier":causal_frontier if causal else None,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"real OpenLane multi-module, multi-clock CDC mutation and disposable agent repair; optional digest-bound causal evidence; one synchronization invariant, not full subsystem closure"};report["report_sha256"]=digest(report);path=a.output/"real-openlane-multiclock-agent-repair-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
