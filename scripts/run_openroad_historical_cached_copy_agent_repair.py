"""Replay OpenROAD's historical portable cached-netlist copy fix."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SUBREPO=ROOT/"analog-digital-chip-design-eda";REPO=Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts");COMMIT="4b688827";SOURCE=Path("flow/scripts/synth_preamble.tcl")
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True);text=(root/SOURCE).read_text();src=out/"cached.v";dst=out/"results.v";src.write_text("module cached; endmodule\n");os.utime(src,(123456789,123456789))
 portable=not re.search(r"^\s*log_cmd exec cp --preserve=timestamps", text, re.MULTILINE) and bool(re.search(r"^\s*log_cmd exec touch -r", text, re.MULTILINE))
 if not portable:
  (out/"stderr.log").write_text("simulated portable-copy failure: cp --preserve=timestamps unsupported\n");return "failed"
 subprocess.run(["cp",str(src),str(dst)],check=True);subprocess.run(["touch","-r",str(src),str(dst)],check=True);return "passed" if dst.read_text()==src.read_text() and dst.stat().st_mtime_ns==src.stat().st_mtime_ns else "failed"
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--backend",choices=("mock","local"),default="mock");a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock":os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip();old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True);fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO));from verification_platform.repository_agent import run_repository_agent;from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openroad-historical-cached-copy-") as td:
  s=Path(td);mut=s/"mutated";rep=s/"repaired"
  for root,text in ((mut,old),(rep,fixed)):q=root/SOURCE;q.parent.mkdir(parents=True);q.write_text(text)
  baseline=execute(mut,a.output/"baseline");src=mut/SOURCE;agent=run_repository_agent(task_id="openroad-cached-copy-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenROAD-flow-scripts commit {COMMIT}","portable cached netlist copy"],failure_context="cached netlist copy must work when cp --preserve=timestamps is unavailable and preserve timestamps via touch -r",repair_before=old,repair_after=fixed,repair_source=src,backend="local",output_root=a.output/"agent");cand=agent.get("patch_candidate",{});repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openroad-cached-copy-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical portable cached-copy repair",str(cand.get("edit_operator","exact_text_replace")));apply_to_copy(src,rep/SOURCE,prop,human_approved=True);repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openroad-historical-cached-copy-agent-repair-report-v1","repository":"OpenROAD-flow-scripts","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":baseline,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if baseline=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenROAD portable cached-copy fix replayed through disposable agent repair; simulated portability contract, not full flow signoff"};report["report_sha256"]=digest(report);path=a.output/"openroad-historical-cached-copy-agent-repair-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
