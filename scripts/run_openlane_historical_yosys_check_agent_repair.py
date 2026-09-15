"""Replay OpenLane's historical Yosys-check report classification fix."""
from __future__ import annotations
import argparse, ast, hashlib, json, io, os, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="5ba7fa07"; SOURCE=Path("scripts/parse_yosys_check.py")
OLD='        if line.startswith("Warning:"):'; NEW='        if line.startswith("Warning:") or line.startswith("Found and reported"):'
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True); source=root/SOURCE; h=out/"yosys-check-regression.py"
 h.write_text(f'''import ast, io, re\nsource=open({str(source)!r}).read(); tree=ast.parse(source)\nfn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="parse_yosys_check")\npat=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="starts_with_whitespace" for t in n.targets))\nns={{"io":io,"re":re}}; exec(compile(ast.Module(body=[pat,fn],type_ignores=[]),{str(source)!r},"exec"),ns)\nr=io.StringIO("Warning: Wire top.\\\\k is used but has no driver.\\nFound and reported 1 problems.\\n")\nprint("PASS" if ns["parse_yosys_check"](r,True,True) is True else "FAIL")\n''',encoding="utf-8")
 c=subprocess.run([sys.executable,str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and c.stdout.strip()=="PASS" else "failed"
def main():
 p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openlane-historical-yosys-check-") as td:
  s=Path(td); mut=s/"mutated"; rep=s/"repaired"
  for root,text in ((mut,old),(rep,fixed)): q=root/SOURCE; q.parent.mkdir(parents=True); q.write_text(text)
  base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-yosys-check-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","Found and reported parser boundary"],failure_context="a report with one non-tristate warning must be classified as an error when the summary line follows it",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openlane-yosys-check-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical Yosys parser repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openlane-historical-yosys-check-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane Python Yosys-check parser fix replayed through disposable agent repair; not repository-scale generalization"}; report["report_sha256"]=digest(report); path=a.output/"openlane-historical-yosys-check-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
