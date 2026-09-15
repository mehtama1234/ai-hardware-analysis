"""Replay OpenLane's historical synth-exploration log parser fix."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SUBREPO=ROOT/"analog-digital-chip-design-eda";REPO=Path("/home/mehtama1/eda-tools/OpenLane");COMMIT="de7e2ca3";SOURCE=Path("scripts/synth_exp/analyze.py")
OLD="""    delay_rx = re.compile(r"Delay\\s+\\=\\s+(\\S+)")
    area_rx = re.compile(r"Area\\s+\\=\\s+(\\S+)")
    gates_rx = re.compile(r"Gates\\s+\\=\\s+(\\S+)")""";NEW="""    delay_rx = re.compile(r"Delay\\s+\\=\\s*(\\S+)")
    area_rx = re.compile(r"Area\\s+\\=\\s*(\\S+)")
    gates_rx = re.compile(r"Gates\\s+\\=\\s*(\\S+)")"""
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True);log=out/"explore.log";log.write_text("USING STRATEGY AREA 1\nnone Delay =10 Area =20 Gates =30\n");report=out/"report.html";c=subprocess.run([sys.executable,str(root/SOURCE),"-o",str(report),str(log)],capture_output=True,text=True);(out/"stdout.log").write_text(c.stdout);(out/"stderr.log").write_text(c.stderr);has_report=report.exists() and "10.0" in report.read_text();return "passed" if c.returncode==0 and has_report else "failed"
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--backend",choices=("mock","local"),default="mock");a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock":os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip();old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True);fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO));from verification_platform.repository_agent import run_repository_agent;from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openlane-historical-synth-analyze-") as td:
  s=Path(td);mut=s/"mutated";rep=s/"repaired"
  for root,text in ((mut,old),(rep,fixed)):q=root/SOURCE;q.parent.mkdir(parents=True);q.write_text(text)
  baseline=execute(mut,a.output/"baseline");src=mut/SOURCE;agent=run_repository_agent(task_id="openlane-synth-analyze-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","synth exploration log parser"],failure_context="synthesis exploration metrics must parse when whitespace around equals is absent",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent");cand=agent.get("patch_candidate",{});repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openlane-synth-analyze-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical synth parser repair",str(cand.get("edit_operator","exact_text_replace")));apply_to_copy(src,rep/SOURCE,prop,human_approved=True);repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openlane-historical-synth-analyze-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":baseline,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if baseline=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane synthesis-log parser fix replayed through disposable agent repair; not full synthesis signoff"};report["report_sha256"]=digest(report);path=a.output/"openlane-historical-synth-analyze-agent-repair-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
