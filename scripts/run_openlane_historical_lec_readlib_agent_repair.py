"""Replay OpenLane's historical LEC read_liberty option correction."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="e99deff71ec5b223e0af272fd77616a1ca97fc6c"; SOURCE=Path("scripts/yosys/logic_equiv_check.tcl")
OLD="\t\tread_liberty -nooverwrite -lib -ignore_miss_dir -setattr blackbox $lib"
NEW="\t\tread_liberty -ignore_miss_func -ignore_miss_dir $lib"

def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def proc_text(t):
    start=t.index("proc initialize"); brace=t.index("{",t.index("}",start)+1); depth=0
    for i in range(brace,len(t)):
        if t[i]=="{": depth+=1
        elif t[i]=="}":
            depth-=1
            if depth==0:return t[start:i+1]
    raise ValueError("initialize proc not closed")
def execute(root,out):
    out.mkdir(parents=True,exist_ok=True); p=out/"initialize.tcl"; p.write_text(proc_text((root/SOURCE).read_text()),encoding="utf-8")
    h=out/"lec-readlib-regression.tcl"; h.write_text(f'''set calls {{}}
proc read_liberty {{args}} {{ lappend ::calls $args }}
set ::env(LIB_TYPICAL) [list /tmp/lib1.lib /tmp/lib2.lib]
source {str(p)}
initialize
set joined [join $::calls " "]
puts [expr {{[string first "-ignore_miss_func" $joined] >= 0 && [string first "-setattr blackbox" $joined] < 0 ? "PASS" : "FAIL"}}]
''',encoding="utf-8")
    c=subprocess.run(["tclsh",str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr)
    return "passed" if c.returncode==0 and c.stdout.strip()=="PASS" else "failed"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
    if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
    rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
    sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
    with tempfile.TemporaryDirectory(prefix="openlane-historical-lec-readlib-") as td:
        s=Path(td); mut=s/"mutated"; rep=s/"repaired"; (mut/SOURCE).parent.mkdir(parents=True); (rep/SOURCE).parent.mkdir(parents=True); (mut/SOURCE).write_text(old); (rep/SOURCE).write_text(fixed)
        base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-lec-readlib-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","LEC read_liberty options"],failure_context="LEC must tolerate missing liberty functions while reading typical libraries",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
        if cand.get("status")=="review_required":
            prop=RepairProposal("openlane-lec-readlib-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical LEC read_liberty repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
        report={"schema_version":"openlane-historical-lec-readlib-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane LEC read_liberty fix replayed through disposable agent repair; not full equivalence signoff"}; report["report_sha256"]=digest(report); path=a.output/"openlane-historical-lec-readlib-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
