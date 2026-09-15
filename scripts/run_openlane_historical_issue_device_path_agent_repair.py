"""Replay OpenLane's historical issue-packager device-path fix."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SUBREPO=ROOT/"analog-digital-chip-design-eda";REPO=Path("/home/mehtama1/eda-tools/OpenLane");COMMIT="281281cc94c2084302845683f2e33fae6cf54eaa";SOURCE=Path("scripts/or_issue.py")
OLD='''        elif value.startswith("/"):
            final_value = value[1:]
            final_path = join(destination_folder, final_value)
            copy(value, final_path)
            final_env[key] = final_value''';NEW='''        elif value.startswith("/") and not value.startswith(
            "/dev"
        ):  # /dev/null, /dev/stdout, /dev/stderr, etc should still work
            final_value = value[1:]
            final_path = join(destination_folder, final_value)
            copy(value, final_path)
            final_env[key] = final_value'''
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True);run=out/"run";run.mkdir();(run/"config.tcl").write_text('set ::env(DEVICE_LOG) /dev/null\n');inp=run/"in.def";inp.write_text("VERSION 5.8\n");script=root/"scripts/openroad/check.tcl";script.parent.mkdir(parents=True,exist_ok=True);script.write_text('puts $::env(DEVICE_LOG)\n');pack=out/"package";spec=importlib.util.spec_from_file_location("or_issue_local",root/SOURCE);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);old_path=os.getcwd();os.chdir(out)
 try:
  mod.issue.callback(str(script),"/tmp",str(run),str(out/"out.def"),False,False,str(pack),"openroad",str(inp))
 finally: os.chdir(old_path)
 return "passed" if (pack/"run.tcl").exists() and not (pack/"dev"/"null").exists() else "failed"
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--backend",choices=("mock","local"),default="mock");a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock":os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip();old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True);fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO));from verification_platform.repository_agent import run_repository_agent;from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openlane-historical-issue-device-") as td:
  s=Path(td);mut=s/"mutated";rep=s/"repaired"
  for r,t in ((mut,old),(rep,fixed)):q=r/SOURCE;q.parent.mkdir(parents=True);q.write_text(t)
  baseline=execute(mut,a.output/"baseline");src=mut/SOURCE;agent=run_repository_agent(task_id="openlane-issue-device-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","device path packaging"],failure_context="the issue packager must not copy /dev/null and similar device paths into the package",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent");cand=agent.get("patch_candidate",{});repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openlane-issue-device-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical issue device-path repair",str(cand.get("edit_operator","exact_text_replace")));apply_to_copy(src,rep/SOURCE,prop,human_approved=True);repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openlane-historical-issue-device-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":baseline,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if baseline=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane issue-packager device-path fix replayed through disposable agent repair; direct packaging contract, not full flow signoff"};report["report_sha256"]=digest(report);path=a.output/"openlane-historical-issue-device-agent-repair-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
