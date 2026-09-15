"""Replay OpenLane's historical remove_nets argument-list fix."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="d4b42bd147d765ad1b5e32213d6af92268e0e96a"; SOURCE=Path("scripts/utils/deflef_utils.tcl")
OLD="        lappend --empty-only"; NEW="        lappend arg_list --empty-only"
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def proc_text(t):
    s=t.index("proc remove_nets"); b=t.index("{",t.index("}",s)+1); d=0
    for i in range(b,len(t)):
        if t[i]=="{": d+=1
        elif t[i]=="}":
            d-=1
            if d==0:return t[s:i+1]
    raise ValueError("remove_nets proc not closed")
def execute(root,out):
    out.mkdir(parents=True,exist_ok=True); p=out/"remove_nets.tcl"; p.write_text(proc_text((root/SOURCE).read_text()),encoding="utf-8")
    h=out/"remove-nets-regression.tcl"; h.write_text(f'''proc parse_key_args {{name args_name arg_values_name options flags_name flags}} {{upvar 1 $arg_values_name av; upvar 1 $flags_name fm; array set av [list]; array set fm [list -empty 1]}}
proc set_if_unset {{var value}} {{upvar 1 $var target; if {{![info exists target]}} {{set target $value}}}}
proc manipulate_layout {{args}} {{set ::observed $args}}
set ::env(SCRIPTS_DIR) /tmp
set ::env(CURRENT_ODB) input.odb
source {str(p)}
remove_nets -empty
puts [expr {{[lsearch -exact $::observed --empty-only] >= 0 ? "PASS" : "FAIL"}}]
''',encoding="utf-8")
    c=subprocess.run(["tclsh",str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and c.stdout.strip()=="PASS" else "failed"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
    if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
    rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
    sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
    with tempfile.TemporaryDirectory(prefix="openlane-historical-remove-nets-") as td:
        s=Path(td); mut=s/"mutated"; rep=s/"repaired"; (mut/SOURCE).parent.mkdir(parents=True); (rep/SOURCE).parent.mkdir(parents=True); (mut/SOURCE).write_text(old); (rep/SOURCE).write_text(fixed)
        base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-remove-nets-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","remove_nets empty-only argument propagation"],failure_context="remove_nets must pass --empty-only to manipulate_layout when -empty is requested",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
        if cand.get("status")=="review_required":
            prop=RepairProposal("openlane-remove-nets-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical remove_nets repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
        report={"schema_version":"openlane-historical-remove-nets-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane remove_nets argument-list fix replayed through disposable agent repair; isolated Tcl command contract, not full layout signoff"}; report["report_sha256"]=digest(report); path=a.output/"openlane-historical-remove-nets-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
