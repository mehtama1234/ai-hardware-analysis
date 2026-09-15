"""Replay OpenLane's historical get_design_path normalization fix."""
from __future__ import annotations
import argparse, ast, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
REVISION="ff5509f6"; COMMIT="41ed0036"; SOURCE=Path("scripts/utils/utils.py")
OLD='    path = os.path.abspath(design) + "/"'; NEW='    path = os.path.abspath(design)'
sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal, apply_to_copy
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
    out.mkdir(parents=True,exist_ok=True); source=root/SOURCE; h=out/"design-path-regression.py"; h.write_text("""import ast\nimport os\nsource = open(SOURCE, encoding='utf8').read()\ntree = ast.parse(source)\nfn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'get_design_path')\nnamespace = {'os': os}\nexec(compile(ast.Module(body=[fn], type_ignores=[]), SOURCE, 'exec'), namespace)\nos.chdir(ROOT)\nresult = namespace['get_design_path']('demo')\nprint('PASS' if result == os.path.abspath('designs/demo') else 'FAIL:' + result)\n""".replace("SOURCE",repr(str(source))).replace("ROOT",repr(str(out/"fixture"))),encoding="utf-8"); (out/"fixture"/"designs"/"demo").mkdir(parents=True,exist_ok=True)
    c=subprocess.run([sys.executable,str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and c.stdout.strip()=="PASS" else "failed"
def main():
 p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 with tempfile.TemporaryDirectory(prefix="openlane-historical-design-path-") as td:
  s=Path(td); mut=s/"mutated"; rep=s/"repaired"
  for root,text in ((mut,old),(rep,fixed)):
   q=root/SOURCE; q.parent.mkdir(parents=True); q.write_text(text)
  base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-design-path-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","get_design_path fallback normalization"],failure_context="get_design_path must return a normalized fallback directory path",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal(requirement_id="openlane-design-path-historical-fix",file=str(cand["source"]),line=int(cand["line"]),before=str(cand["before"]),after=str(cand["after"]),rationale="benchmark-only historical OpenLane path repair",edit_operator=str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openlane-historical-design-path-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"canonical_fixed_source_sha256":hashlib.sha256(fixed.encode()).hexdigest(),"backend":a.backend,"task_id":"openlane-design-path-historical-fix","baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane Python path fix replayed through disposable agent repair; not repository-scale generalization"}
 report["report_sha256"]=digest(report); path=a.output/"openlane-historical-design-path-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"historical_fix_commit":COMMIT,"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
def execute(root,out):
    out.mkdir(parents=True,exist_ok=True)
    source=root/SOURCE
    fixture=out/"fixture"
    fixture.joinpath("designs","demo").mkdir(parents=True,exist_ok=True)
    harness=out/"design-path-regression.py"
    harness.write_text(
        "import os\nimport runpy\n"
        f"namespace = runpy.run_path({str(source)!r})\n"
        f"os.chdir({str(fixture)!r})\n"
        "result = namespace['get_design_path']('designs/demo')\n"
        "print('PASS' if result == os.path.abspath('designs/demo') else 'FAIL:' + result)\n",
        encoding="utf-8",
    )
    c=subprocess.run([sys.executable,str(harness)],cwd=out,capture_output=True,text=True)
    (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr)
    return "passed" if c.returncode==0 and c.stdout.strip()=="PASS" else "failed"

if __name__=="__main__": raise SystemExit(main())
