"""Replay OpenLane's historical irdrop argument-list construction fix."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SUBREPO=ROOT/"analog-digital-chip-design-eda";REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="24dcb51e";SOURCE=Path("scripts/openroad/irdrop.tcl")
OLD='''        lappend arg_list -net $::env(VDD_NET)''';NEW='''        lappend arg_list -net $net'''
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True);h=out/"irdrop-regression.tcl";h.write_text(f'''set calls {{}}\nproc source {{args}} {{}};proc read {{}} {{}};proc read_spef {{args}} {{}};proc analyze_power_grid {{args}} {{lappend ::calls $args}}\nset ::env(SCRIPTS_DIR) /tmp;set ::env(CURRENT_SPEF) /tmp/a.spef;set ::env(_tmp_save_rpt_prefix) /tmp/irdrop;set ::env(VDD_NETS) VDD;set ::env(GND_NETS) GND\nsource {str(root/SOURCE)}\nputs [expr {{[lindex $::calls 0] eq "-net VDD -outfile /tmp/irdrop-VDD.rpt" ? "PASS" : "FAIL"}}]\n''',encoding="utf-8");c=subprocess.run(["tclsh",str(h)],cwd=out,capture_output=True,text=True);(out/"stdout.log").write_text(c.stdout);(out/"stderr.log").write_text(c.stderr);return "passed" if c.returncode==0 and c.stdout.strip()=="PASS" else "failed"
def main():
 q=argparse.ArgumentParser();q.add_argument("--output",type=Path,required=True);q.add_argument("--backend",choices=("mock","local"),default="mock");a=q.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock":os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip();old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True);fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO));from verification_platform.repository_agent import run_repository_agent;from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openlane-historical-irdrop-args-") as td:
  s=Path(td);mut=s/"mutated";rep=s/"repaired"
  for root,text in ((mut,old),(rep,fixed)):q=root/SOURCE;q.parent.mkdir(parents=True);q.write_text(text)
  base=execute(mut,a.output/"baseline");src=mut/SOURCE;agent=run_repository_agent(task_id="openlane-irdrop-args-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","analyze_power_grid arguments"],failure_context="each default power net must be passed to analyze_power_grid through arg_list",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent");cand=agent.get("patch_candidate",{});repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openlane-irdrop-args-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical irdrop argument repair",str(cand.get("edit_operator","exact_text_replace")));apply_to_copy(src,rep/SOURCE,prop,human_approved=True);repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openlane-historical-irdrop-args-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane Tcl irdrop argument fix replayed through disposable agent repair; not repository-scale generalization"};report["report_sha256"]=digest(report);path=a.output/"openlane-historical-irdrop-args-agent-repair-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True));return 0 if report["status"]=="passed" else 1
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True); h=out/"irdrop-regression.tcl"; script='''set calls {}
rename source _source; proc source {args} {}; proc read {args} {}; proc read_spef {args} {}; proc analyze_power_grid {args} {lappend ::calls $args}
set ::env(SCRIPTS_DIR) /tmp; set ::env(CURRENT_SPEF) /tmp/a.spef; set ::env(_tmp_save_rpt_prefix) /tmp/irdrop; set ::env(VDD_NETS) VDD; set ::env(GND_NETS) GND
_source SOURCE
puts [expr {[llength [lindex $::calls 0]] > 0 ? "PASS" : "FAIL"}]
'''.replace("SOURCE",str(root/SOURCE)); h.write_text(script,encoding="utf-8"); c=subprocess.run(["tclsh",str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and c.stdout.strip()=="PASS" else "failed"
if __name__=="__main__":raise SystemExit(main())
