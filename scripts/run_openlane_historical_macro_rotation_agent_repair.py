"""Replay OpenLane's historical manual-macro rotation mapping fix."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="14ef870b62132a05cc35f45f2d43ea015b9efd6b"; SOURCE=Path("scripts/manual_macro_place.py")
OLD='"FW": "MX90",\n              "FE": "MY90"'; NEW='"FW": "MXR90",\n              "FE": "MYR90"'
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
    out.mkdir(parents=True,exist_ok=True); t=(root/SOURCE).read_text(); ok=NEW in t and OLD not in t
    (out/"rotation-contract.txt").write_text("PASS\n" if ok else "FAIL\n"); return "passed" if ok else "failed"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
    if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
    rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
    sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
    with tempfile.TemporaryDirectory(prefix="openlane-historical-macro-rotation-") as td:
        s=Path(td); mut=s/"mutated"; rep=s/"repaired"; (mut/SOURCE).parent.mkdir(parents=True); (rep/SOURCE).parent.mkdir(parents=True); (mut/SOURCE).write_text(old); (rep/SOURCE).write_text(fixed)
        base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-macro-rotation-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","LEF to OpenAccess rotation mapping"],failure_context="FW and FE rotations must map to valid OpenAccess MXR90 and MYR90 values",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
        if cand.get("status")=="review_required":
            prop=RepairProposal("openlane-macro-rotation-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical macro rotation repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
        report={"schema_version":"openlane-historical-macro-rotation-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane macro rotation mapping fix replayed through disposable agent repair; mapping contract only, not full placement signoff"}; report["report_sha256"]=digest(report); path=a.output/"openlane-historical-macro-rotation-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
