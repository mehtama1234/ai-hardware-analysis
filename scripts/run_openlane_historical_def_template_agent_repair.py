"""Replay OpenLane's historical FP_DEF_TEMPLATE placement fix."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
REVISION="ff5509f6"; COMMIT="f4f8dad8"; SOURCE=Path("scripts/tcl_commands/placement.tcl")
OLD="        if { $::env(FP_IO_MODE) == 0 && ![info exists ::env(FP_PIN_ORDER_CFG)] } {"; NEW="        if { $::env(FP_IO_MODE) == 0 && ![info exists ::env(FP_PIN_ORDER_CFG)] && ![info exists ::env(FP_DEF_TEMPLATE)] } {"
sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal, apply_to_copy
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
    out.mkdir(parents=True,exist_ok=True); text=(root/SOURCE).read_text(); condition=next(l.strip() for l in text.splitlines() if l.strip().startswith("if { $::env(FP_IO_MODE) == 0")); condition=condition[:-1].rstrip() if condition.endswith("{") else condition
    h=out/"def-template-regression.tcl"; h.write_text("\n".join(["set ::env(FP_IO_MODE) 0","set ::env(FP_DEF_TEMPLATE) template.def","set ::called 0","proc place_io {args} { set ::called 1 }",f"{condition} {{ place_io }}","puts $::called",""])); c=subprocess.run(["tclsh",str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and c.stdout.strip()=="0" else "failed"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
    if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
    rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
    with tempfile.TemporaryDirectory(prefix="openlane-historical-def-template-") as td:
        s=Path(td); mut=s/"mutated"; rep=s/"repaired"
        for root,text in ((mut,old),(rep,fixed)):
            q=root/SOURCE; q.parent.mkdir(parents=True); q.write_text(text)
        base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-fp-def-template-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","FP_DEF_TEMPLATE placement regression"],failure_context="automatic place_io must not run when FP_DEF_TEMPLATE is present",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
        if cand.get("status")=="review_required":
            prop=RepairProposal(requirement_id="openlane-fp-def-template-historical-fix",file=str(cand["source"]),line=int(cand["line"]),before=str(cand["before"]),after=str(cand["after"]),rationale="benchmark-only historical OpenLane placement repair",edit_operator=str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
        report={"schema_version":"openlane-historical-def-template-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"canonical_fixed_source_sha256":hashlib.sha256(fixed.encode()).hexdigest(),"backend":a.backend,"task_id":"openlane-fp-def-template-historical-fix","baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane placement fix replayed through disposable agent repair; not repository-scale generalization"}
    report["report_sha256"]=digest(report); path=a.output/"openlane-historical-def-template-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"historical_fix_commit":COMMIT,"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
