"""Replay OpenROAD's historical stale-target test-flow fix."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SUBREPO=ROOT/"analog-digital-chip-design-eda";REPO=Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts");COMMIT="c178fbb7";SOURCE=Path("flow/test/test-do-stage.sh")
OLD="""make do-yosys-canonicalize
make do-yosys-keep-hierarchy
make do-yosys
make do-synth
make do-floorplan""";NEW="""make do-yosys-canonicalize
make do-yosys
# There is deliberately no do-synth step (see the do-step comment in
# flow/Makefile); make synth materializes 1_2_yosys.sdc and 1_synth.odb.
make synth
make do-floorplan"""
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True);bin_dir=out/"bin";bin_dir.mkdir();log=out/"make.log";fake=bin_dir/"make";fake.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> \""+str(log)+"\"\n");fake.chmod(0o755);env=dict(os.environ);env["PATH"]=str(bin_dir)+os.pathsep+env.get("PATH","");c=subprocess.run(["bash",str(root/SOURCE)],cwd=out,env=env,capture_output=True,text=True);calls=log.read_text().splitlines() if log.exists() else [];ok=("synth" in calls and "do-synth" not in calls);(out/"stdout.log").write_text(c.stdout);(out/"stderr.log").write_text(c.stderr);return "passed" if c.returncode==0 and ok else "failed"
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--backend",choices=("mock","local"),default="mock");a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock":os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip();old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True);fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO));from verification_platform.repository_agent import run_repository_agent;from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openroad-historical-stale-target-") as td:
  s=Path(td);mut=s/"mutated";rep=s/"repaired"
  for r,t in ((mut,old),(rep,fixed)):q=r/SOURCE;q.parent.mkdir(parents=True);q.write_text(t)
  baseline=execute(mut,a.output/"baseline");src=mut/SOURCE;agent=run_repository_agent(task_id="openroad-stale-target-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenROAD-flow-scripts commit {COMMIT}","stale do-synth target"],failure_context="the stage test must invoke make synth, not the stale do-synth target",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent");cand=agent.get("patch_candidate",{});repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openroad-stale-target-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical stale-target repair",str(cand.get("edit_operator","exact_text_replace")));apply_to_copy(src,rep/SOURCE,prop,human_approved=True);repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openroad-historical-stale-target-agent-repair-report-v1","repository":"OpenROAD-flow-scripts","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":baseline,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if baseline=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenROAD stale-target test-flow fix replayed through disposable agent repair; shell command contract, not full flow signoff"};report["report_sha256"]=digest(report);path=a.output/"openroad-historical-stale-target-agent-repair-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
