"""Replay OpenLane's historical Magic DRC file-handle fix."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SUBREPO=ROOT/"analog-digital-chip-design-eda";REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="1d46ea5f";SOURCE=Path("scripts/drc_rosetta.py")
OLD="magic_to_tr(open(magic_input).read(), f)";NEW="magic_to_tr(open(magic_input), f)"
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True);src=root/SOURCE;inp=out/"magic.drc";inp.write_text("""----------------------------------------\nViolation type: P-diff distance to N-tap must be < 15.0um (LU.3)\n  bbox = ( 17.990, 21.995 ) - ( 18.265, 22.995 )\n""")
 h=out/"drc-regression.py";h.write_text(f'''import runpy\nns=runpy.run_path({str(src)!r});inp={str(inp)!r};open(inp,"w").write(ns["MAGIC_EXAMPLE"]);out={str(out/"result.tr.drc")!r};ns["magic_to_tr_cmd"].callback(out,inp)\nprint("PASS" if "violation type" in open(out).read().lower() else "FAIL")\n''',encoding="utf-8");c=subprocess.run([sys.executable,str(h)],cwd=out,capture_output=True,text=True);(out/"stdout.log").write_text(c.stdout);(out/"stderr.log").write_text(c.stderr);return "passed" if c.returncode==0 and c.stdout.strip()=="PASS" else "failed"
def main():
 q=argparse.ArgumentParser();q.add_argument("--output",type=Path,required=True);q.add_argument("--backend",choices=("mock","local"),default="mock");a=q.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock":os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip();old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True);fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO));from verification_platform.repository_agent import run_repository_agent;from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openlane-historical-drc-file-") as td:
  s=Path(td);mut=s/"mutated";rep=s/"repaired"
  for root,text in ((mut,old),(rep,fixed)):q=root/SOURCE;q.parent.mkdir(parents=True);q.write_text(text)
  base=execute(mut,a.output/"baseline");src=mut/SOURCE;agent=run_repository_agent(task_id="openlane-drc-file-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","Magic DRC input handle"],failure_context="the Magic-to-TritonRoute command must pass a file handle to the line-oriented parser",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent");cand=agent.get("patch_candidate",{});repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openlane-drc-file-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical DRC input repair",str(cand.get("edit_operator","exact_text_replace")));apply_to_copy(src,rep/SOURCE,prop,human_approved=True);repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openlane-historical-drc-file-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane Python DRC input-handle fix replayed through disposable agent repair; not repository-scale generalization"};report["report_sha256"]=digest(report);path=a.output/"openlane-historical-drc-file-agent-repair-report.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True));return 0 if report["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
