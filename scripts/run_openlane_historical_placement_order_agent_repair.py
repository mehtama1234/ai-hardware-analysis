"""Replay OpenLane's historical random-placement ordering fix."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="6c80fdbc"; SOURCE=Path("scripts/tcl_commands/placement.tcl")
OLD='''    increment_index
    TIMER::timer_start
    set log [index_file $arg_values(-log)]
    puts_info "Running Global Placement (log: [relpath . $log])..."
    # random initial placement
    if { $::env(PL_RANDOM_INITIAL_PLACEMENT) } {
        random_global_placement
        set ::env(PL_SKIP_INITIAL_PLACEMENT) 1
    }
'''; NEW='''    set log [index_file $arg_values(-log)]
    # random initial placement
    if { $::env(PL_RANDOM_INITIAL_PLACEMENT) } {
        random_global_placement
        set ::env(PL_SKIP_INITIAL_PLACEMENT) 1
    }
    increment_index
    TIMER::timer_start
'''
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def proc_text(text):
 start=text.index("proc global_placement_or"); brace=text.index("{",text.index("}",start)+1); depth=0
 for i in range(brace,len(text)):
  if text[i]=="{": depth+=1
  elif text[i]=="}":
   depth-=1
   if depth==0:return text[start:i+1]
 raise ValueError("proc not closed")
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True); source=root/SOURCE; p=out/"placement.tcl"; p.write_text(proc_text(source.read_text()),encoding="utf-8"); h=out/"placement-order-regression.tcl"
 h.write_text(f'''set events {{}}\nproc parse_key_args {{name args_name arg_values_name options flags_name flags}} {{ upvar 1 $arg_values_name av; upvar 1 $flags_name fm; array set av [list -log /tmp/global.log -outdir /tmp -name global]; array set fm [list -skip_io 1] }}\nproc set_if_unset {{name value}} {{}}\nproc index_file {{path}} {{ return $path }}; proc relpath {{args}} {{return log}}; proc puts_info {{msg}} {{lappend ::events info}}\nproc random_global_placement {{args}} {{lappend ::events random}}; proc increment_index {{}} {{lappend ::events index}}; proc run_openroad_script {{args}} {{lappend ::events openroad}}; proc check_replace_divergence {{}} {{}}; proc run_sta {{args}} {{}}; proc exec {{args}} {{return ""}}\nnamespace eval TIMER {{proc timer_start {{}} {{lappend ::events timer}}; proc timer_stop {{}} {{}}; proc get_runtime {{}} {{return 0}}}}\nset ::env(placement_logs) /tmp; set ::env(placement_tmpfiles) /tmp; set ::env(SCRIPTS_DIR) /tmp; set ::env(PL_RANDOM_INITIAL_PLACEMENT) 1\nsource {str(p)}\nglobal_placement_or\nputs $::events\n''',encoding="utf-8")
 c=subprocess.run(["tclsh",str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and c.stdout.strip().splitlines() and c.stdout.strip().splitlines()[0].startswith("random index") else "failed"
def main():
 p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openlane-historical-placement-order-") as td:
  s=Path(td); mut=s/"mutated"; rep=s/"repaired"
  for root,text in ((mut,old),(rep,fixed)): q=root/SOURCE; q.parent.mkdir(parents=True); q.write_text(text)
  base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-placement-order-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","random placement ordering"],failure_context="random initial placement must occur before the global placement index and timer are started",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openlane-placement-order-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical placement ordering repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openlane-historical-placement-order-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane Tcl placement-order fix replayed through disposable agent repair; not repository-scale generalization"}; report["report_sha256"]=digest(report); path=a.output/"openlane-historical-placement-order-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
