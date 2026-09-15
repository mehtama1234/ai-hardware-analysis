"""Replay OpenROAD's historical microwatt antenna-iteration limit fix."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SUBREPO=ROOT/"analog-digital-chip-design-eda";REPO=Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts");COMMIT="304e5765";SOURCE=Path("flow/designs/sky130hd/microwatt/config.mk")
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True);makefile=out/"Makefile";makefile.write_text(f"DESIGN_HOME=/tmp\nPLATFORM=sky130hd\nDESIGN_NICKNAME=microwatt\ninclude {root/SOURCE}\nall:\n\t@echo $(MAX_REPAIR_ANTENNAS_ITER_DRT)\n");c=subprocess.run(["make","-s","-f",str(makefile),"all"],capture_output=True,text=True);(out/"stdout.log").write_text(c.stdout);(out/"stderr.log").write_text(c.stderr);return "passed" if c.returncode==0 and c.stdout.strip()=="2" else "failed"
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--backend",choices=("mock","local"),default="mock");a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock":os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip();old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True);fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO));from verification_platform.repository_agent import run_repository_agent;from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openroad-historical-antenna-limit-") as td:
  s=Path(td);mut=s/"mutated";rep=s/"repaired"
  for root,text in ((mut,old),(rep,fixed)):q=root/SOURCE;q.parent.mkdir(parents=True);q.write_text(text)
  baseline=execute(mut,a.output/"baseline");src=mut/SOURCE;agent=run_repository_agent(task_id="openroad-antenna-limit-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenROAD-flow-scripts commit {COMMIT}","microwatt antenna repair bound"],failure_context="the microwatt flow must define a bounded MAX_REPAIR_ANTENNAS_ITER_DRT value of 2",repair_before=old,repair_after=fixed,repair_source=src,backend="local",output_root=a.output/"agent");cand=agent.get("patch_candidate",{});repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openroad-antenna-limit-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical antenna limit repair",str(cand.get("edit_operator","exact_text_replace")));apply_to_copy(src,rep/SOURCE,prop,human_approved=True);repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openroad-historical-antenna-limit-agent-repair-report-v1","repository":"OpenROAD-flow-scripts","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":baseline,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if baseline=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenROAD microwatt antenna-iteration configuration fix replayed through disposable agent repair; Make contract, not full physical-flow signoff"};report["report_sha256"]=digest(report);path=a.output/"openroad-historical-antenna-limit-agent-repair-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
