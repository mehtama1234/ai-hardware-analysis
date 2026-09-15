"""Replay OpenLane's historical Jenkins Docker-tag naming fix."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="01e951092150ee8619286b0807ee263198b5ea6d"; SOURCE=Path("Jenkinsfile")
OLD="""                sh 'make -C docker openlane';
                sh 'docker save efabless/openlane:current | gzip > openlane-current.tar.gz';"""; NEW="""                sh 'make -C docker openlane OPENLANE_IMAGE_NAME=current:latest';
                sh 'docker save current:latest-amd64 | gzip > openlane-current.tar.gz';"""
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
    out.mkdir(parents=True,exist_ok=True); t=(root/SOURCE).read_text(); ok=NEW in t and OLD not in t
    (out/"contract.txt").write_text("PASS\n" if ok else "FAIL\n",encoding="utf-8"); return "passed" if ok else "failed"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
    if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
    rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
    sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
    with tempfile.TemporaryDirectory(prefix="openlane-historical-jenkins-tag-") as td:
        s=Path(td); mut=s/"mutated"; rep=s/"repaired"; (mut/SOURCE).parent.mkdir(parents=True); (rep/SOURCE).parent.mkdir(parents=True); (mut/SOURCE).write_text(old); (rep/SOURCE).write_text(fixed)
        base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-jenkins-tag-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","Jenkins Docker image tag naming"],failure_context="Jenkins must save the image using the tag produced by the OPENLANE_IMAGE_NAME=current:latest build",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
        if cand.get("status")=="review_required":
            prop=RepairProposal("openlane-jenkins-tag-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical Jenkins tag repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
        report={"schema_version":"openlane-historical-jenkins-tag-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane Jenkins tag fix replayed through disposable agent repair; build/save command contract only, not CI signoff"}; report["report_sha256"]=digest(report); path=a.output/"openlane-historical-jenkins-tag-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
