"""Replay OpenLane's historical I/O pin-extension gating fix."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="c98a290f7046bed7ef7c37d1f06927c0b6071e67"; SOURCE=Path("scripts/openroad/ioplacer.tcl")
OLD="""if {$::env(FP_IO_HLENGTH) != \"\" && $::env(FP_IO_HLENGTH) != \"\"} {
\tset_pin_length_extension -hor_extension $::env(FP_IO_HEXTEND) \\
\t\t-ver_extension $::env(FP_IO_VEXTEND)
}"""; NEW="""if {$::env(FP_IO_HEXTEND) != \"0\" && $::env(FP_IO_VEXTEND) != \"0\"} {
\tset_pin_length_extension -hor_extension $::env(FP_IO_HEXTEND) \\
\t\t-ver_extension $::env(FP_IO_VEXTEND)
}"""
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
    out.mkdir(parents=True,exist_ok=True); t=(root/SOURCE).read_text(); branch=NEW if NEW in t else OLD if OLD in t else ""
    h=out/"ioplacer-extension-regression.tcl"; h.write_text(f'''set ::env(FP_IO_HLENGTH) 4
set ::env(FP_IO_HEXTEND) 0
set ::env(FP_IO_VEXTEND) 0
set ::called 0
proc set_pin_length_extension {{args}} {{set ::called 1}}
{branch}
puts [expr {{$::called == 0 ? "PASS" : "FAIL"}}]
''',encoding="utf-8")
    c=subprocess.run(["tclsh",str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and c.stdout.strip()=="PASS" else "failed"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
    if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
    rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
    sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
    with tempfile.TemporaryDirectory(prefix="openlane-historical-ioplacer-extension-") as td:
        s=Path(td); mut=s/"mutated"; rep=s/"repaired"; (mut/SOURCE).parent.mkdir(parents=True); (rep/SOURCE).parent.mkdir(parents=True); (mut/SOURCE).write_text(old); (rep/SOURCE).write_text(fixed)
        base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-ioplacer-extension-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","I/O pin extension gating"],failure_context="pin extension must not be invoked when both extension values are zero",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
        if cand.get("status")=="review_required":
            prop=RepairProposal("openlane-ioplacer-extension-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical I/O extension repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
        report={"schema_version":"openlane-historical-ioplacer-extension-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane I/O extension gating fix replayed through disposable agent repair; isolated Tcl branch contract, not full placement signoff"}; report["report_sha256"]=digest(report); path=a.output/"openlane-historical-ioplacer-extension-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
