"""Replay OpenLane's historical empty-glob configuration fix."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SUBREPO=ROOT/"analog-digital-chip-design-eda";REPO=Path("/home/mehtama1/eda-tools/OpenLane");COMMIT="1c950442";SOURCE=Path("scripts/config/tcl.py")
OLD="""                files_escaped = [file.replace("$", r"\\$") for file in files]
                value = " ".join(files_escaped)""";NEW="""                if len(files) != 0:
                    files_escaped = [file.replace("$", r"\\$") for file in files]
                    value = " ".join(files_escaped)"""
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True);spec=importlib.util.spec_from_file_location("openlane_config",root/SOURCE);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);base=str(out/"missing")+"/artifact*.v";result=mod.process_string("ref::$ROOT/missing/artifact*.v",mod.State({"ROOT":str(out)}));(out/"resolved-path.txt").write_text(result+"\n");return "passed" if result==base else "failed"
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--backend",choices=("mock","local"),default="mock");a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock":os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=__import__("subprocess").check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip();import subprocess;old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True);fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO));from verification_platform.repository_agent import run_repository_agent;from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openlane-historical-config-glob-") as td:
  s=Path(td);mut=s/"mutated";rep=s/"repaired"
  for r,t in ((mut,old),(rep,fixed)):q=r/SOURCE;q.parent.mkdir(parents=True);q.write_text(t)
  baseline=execute(mut,a.output/"baseline");src=mut/SOURCE;agent=run_repository_agent(task_id="openlane-config-glob-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","empty configuration glob"],failure_context="an unresolved glob must remain a path instead of becoming an empty string",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent");cand=agent.get("patch_candidate",{});repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openlane-config-glob-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical empty-glob repair",str(cand.get("edit_operator","exact_text_replace")));apply_to_copy(src,rep/SOURCE,prop,human_approved=True);repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openlane-historical-config-glob-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":baseline,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if baseline=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane empty-glob configuration fix replayed through disposable agent repair; direct parser contract, not full flow signoff"};report["report_sha256"]=digest(report);path=a.output/"openlane-historical-config-glob-agent-repair-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
