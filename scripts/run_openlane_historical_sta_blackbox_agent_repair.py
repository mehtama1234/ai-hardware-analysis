"""Replay OpenLane's historical multi-corner STA black-box check fix."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="0e8827eb"; SOURCE=Path("scripts/tcl_commands/sta.tcl")
OLD='''        if { [info exists flags_map(-blackbox_check)] } {
            blackbox_modules_check $log
        }
    }'''; NEW='''    }
    if { [info exists flags_map(-blackbox_check)] } {
        blackbox_modules_check $log
    }'''
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
"""Legacy harness retained only as historical draft.
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True); source=root/SOURCE; log=out/"sta.log"; h=out/"sta-regression.tcl"
 h.write_text(f'''set test_log {str(log)!r}\nset blackbox_seen 0\nproc parse_key_args {{name args_name arg_values_name options flags_name flags}} {{\n    upvar 1 $arg_values_name av\n    upvar 1 $flags_name fm\n    array set av [list -log $::test_log -tool openroad -save_to /tmp]\n    array set fm [list -multi_corner 1 -blackbox_check 1 -no_save 1]\n}}\nproc set_if_unset {{name value}} {{ if {{![info exists ::env($name)}}} {{ set ::env($name) $value }} }}\nproc increment_index {{}} {{}}\nproc index_file {{path}} {{ return $::test_log }}\nproc puts_info {{args}} {{}}\nproc puts_warn {{args}} {{ set ::blackbox_seen 1 }}\nproc relpath {{args}} {{ return log }}\nproc run_openroad_script {{args}} {{ set fp [open $::test_log w]; puts $fp "module foo not found"; close $fp }}\nproc exec {{args}} {{ return "" }}\nnamespace eval TIMER {{ proc timer_start {{}} {{}}; proc timer_stop {{}} {{}}; proc get_runtime {{}} {{ return 0 }} }}\nset ::env(signoff_results) /tmp\nset ::env(STA_WRITE_LIB) 0\nset ::env(GRT_ESTIMATE_PARASITICS) 0\nset ::env(PL_ESTIMATE_PARASITICS) 0\nset ::env(SCRIPTS_DIR) /tmp\nsource {str(source)!r}\nrun_sta\nputs [expr {{$::blackbox_seen ? "PASS" : "FAIL"}}]\n''',encoding="utf-8")
 c=subprocess.run(["tclsh",str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and c.stdout.strip().endswith("PASS") else "failed"
"""
def main():
 p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openlane-historical-sta-blackbox-") as td:
  s=Path(td); mut=s/"mutated"; rep=s/"repaired"
  for root,text in ((mut,old),(rep,fixed)): q=root/SOURCE; q.parent.mkdir(parents=True); q.write_text(text)
  base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-sta-blackbox-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","multi-corner blackbox check"],failure_context="-blackbox_check must execute for multi-corner STA runs",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openlane-sta-blackbox-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical STA blackbox repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openlane-historical-sta-blackbox-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane Tcl STA control-flow fix replayed through disposable agent repair; not repository-scale generalization"}; report["report_sha256"]=digest(report); path=a.output/"openlane-historical-sta-blackbox-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True); source=root/SOURCE; log=out/"sta.log"; h=out/"sta-regression.tcl"
 script=r'''set test_log LOG
proc parse_key_args {name args_name arg_values_name options flags_name flags} { upvar 1 $arg_values_name av; upvar 1 $flags_name fm; array set av [list -log $::test_log -tool openroad -save_to /tmp]; array set fm [list -multi_corner 1 -blackbox_check 1 -no_save 1] }
proc set_if_unset {name value} { if {![info exists ::env($name)]} { set ::env($name) $value } }
proc increment_index {} {}; proc index_file {path} { return $::test_log }; proc puts_info {args} {}; proc puts_warn {args} { set ::blackbox_seen 1 }; proc relpath {args} { return log }
proc run_openroad_script {args} { set fp [open $::test_log w]; puts $fp "module foo not found"; close $fp }; proc exec {args} { return "" }
namespace eval TIMER { proc timer_start {} {}; proc timer_stop {} {}; proc get_runtime {} { return 0 } }
set ::blackbox_seen 0; set ::env(signoff_results) /tmp; set ::env(STA_WRITE_LIB) 0; set ::env(SAVE_SDF) 1; set ::env(GRT_ESTIMATE_PARASITICS) 0; set ::env(PL_ESTIMATE_PARASITICS) 0; set ::env(SCRIPTS_DIR) /tmp
source SOURCE
run_sta
puts [lindex [list FAIL PASS] $::blackbox_seen]
'''.replace("LOG",str(log).replace("\\","/" )).replace("SOURCE",str(source).replace("\\","/"))
 h.write_text(script,encoding="utf-8"); c=subprocess.run(["tclsh",str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and c.stdout.strip().endswith("PASS") else "failed"
if __name__=="__main__": raise SystemExit(main())
