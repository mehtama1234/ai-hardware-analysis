"""Replay OpenLane's historical Verilator define-variable fix."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="b5b0bbdf"; SOURCE=Path("scripts/tcl_commands/synthesis.tcl")
OLD='            set defines "$defines +define+$override"'; NEW='            set defines "$defines +define+$define"'
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def proc_text(text):
 start=text.index("proc run_verilator"); brace=text.index("{",text.index("}",start)+1); depth=0
 for i in range(brace,len(text)):
  if text[i]=="{": depth+=1
  elif text[i]=="}":
   depth-=1
   if depth==0:return text[start:i+1]
 raise ValueError("proc not closed")
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True); source=root/SOURCE; p=out/"run-verilator.tcl"; p.write_text(proc_text(source.read_text()),encoding="utf-8"); h=out/"linter-defines-regression.tcl"
 h.write_text(f'''set captured {{}}\nproc puts_warn {{args}} {{}}; proc puts_info {{args}} {{}}; proc puts_err {{args}} {{}}; proc relpath {{args}} {{return log}}\nproc try_exec {{args}} {{ set ::captured $args }}\nproc exec {{args}} {{ return "" }}\nset ::env(PDK) bad; set ::env(STD_CELL_LIBRARY) bad; set ::env(PDK_ROOT) /tmp; set ::env(STD_CELL_LIBRARY_OPT) bad\nset ::env(synthesis_logs) /tmp; set ::env(LINTER_INCLUDE_PDK_MODELS) 0; set ::env(VERILOG_FILES) [list top.sv]; set ::env(LINTER_RELATIVE_INCLUDES) 0\nset ::env(LINTER_DEFINES) [list FOO BAR]; set ::env(TERMINAL_OUTPUT) /dev/null; set ::env(DESIGN_NAME) top; set ::env(QUIT_ON_LINTER_ERRORS) 0; set ::env(QUIT_ON_LINTER_WARNINGS) 0\nsource {str(p)}\nrun_verilator\nputs [expr {{[string first "+define+FOO" [join $::captured " "]] >= 0 && [string first "+define+BAR" [join $::captured " "]] >= 0 ? "PASS" : "FAIL"}}]\n''',encoding="utf-8")
 h.write_text(h.read_text().replace('proc exec {args} { return "" }','proc exec {args} { return 0 }'),encoding="utf-8")
 c=subprocess.run(["tclsh",str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and c.stdout.strip().endswith("PASS") else "failed"
def main():
 p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openlane-historical-linter-defines-") as td:
  s=Path(td); mut=s/"mutated"; rep=s/"repaired"
  for root,text in ((mut,old),(rep,fixed)): q=root/SOURCE; q.parent.mkdir(parents=True); q.write_text(text)
  base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-linter-defines-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","Verilator linter defines"],failure_context="each LINTER_DEFINES entry must be emitted as a +define+ macro argument",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openlane-linter-defines-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical linter-defines repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openlane-historical-linter-defines-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane Tcl linter-define fix replayed through disposable agent repair; not repository-scale generalization"}; report["report_sha256"]=digest(report); path=a.output/"openlane-historical-linter-defines-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
OLD="""    set defines ""
    if { [info exists ::env(LINTER_DEFINES)] } {
        foreach define $::env(LINTER_DEFINES) {
            set defines "$defines +define+$override"
        }
    } elseif { [info exists ::env(SYNTH_DEFINES)] } {
        foreach define $::env(SYNTH_DEFINES) {
            set defines "$defines +define+$override"
        }
    }
"""
NEW="""    set defines ""
    if { [info exists ::env(LINTER_DEFINES)] } {
        foreach define $::env(LINTER_DEFINES) {
            set defines "$defines +define+$define"
        }
    } elseif { [info exists ::env(SYNTH_DEFINES)] } {
        foreach define $::env(SYNTH_DEFINES) {
            set defines "$defines +define+$define"
        }
    }
"""
if __name__=="__main__": raise SystemExit(main())
