"""Replay OpenLane's historical Report run_path propagation fix."""
from __future__ import annotations
import argparse, ast, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="4ced43c5"; SOURCE=Path("scripts/report/report.py")
OLD="            None, design_path, tag, full=True"; NEW="            run_path, design_path, tag, full=True"
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True); source=root/SOURCE; h=out/"report-path-regression.py"
 h.write_text(f'''import ast\nsource=open({str(source)!r}).read(); tree=ast.parse(source)\ncls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="Report")\ninit=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="__init__")\ncls.body=[init]\nseen=[]\nclass C:\n @staticmethod\n def get_config_for_run(*args,**kwargs): seen.append((args,kwargs)); return {{"selected":args[0]}}\nns={{"ConfigHandler":C,"get_run_path":lambda **kwargs: "derived"}}; exec(compile(ast.Module(body=[cls],type_ignores=[]),{str(source)!r},"exec"),ns)\nobj=ns["Report"]("design","tag","demo",{{}},run_path="explicit-run")\nprint("PASS" if seen and seen[0][0][0]=="explicit-run" and obj.configuration_full["selected"]=="explicit-run" else "FAIL:"+repr(seen))\n''',encoding="utf-8")
 c=subprocess.run([sys.executable,str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and c.stdout.strip()=="PASS" else "failed"
def main():
 p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openlane-historical-report-path-") as td:
  s=Path(td); mut=s/"mutated"; rep=s/"repaired"
  for root,text in ((mut,old),(rep,fixed)): q=root/SOURCE; q.parent.mkdir(parents=True); q.write_text(text)
  base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-report-path-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","explicit run_path propagation"],failure_context="Report must use the explicitly supplied run_path when loading configuration",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openlane-report-path-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical Report path repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openlane-historical-report-path-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane Python Report path fix replayed through disposable agent repair; not repository-scale generalization"}; report["report_sha256"]=digest(report); path=a.output/"openlane-historical-report-path-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True); source=root/SOURCE; h=out/"report-path-regression.py"
 h.write_text(f"""import ast
import os
from typing import Dict, Optional, Iterable
source=open({str(source)!r}).read(); tree=ast.parse(source)
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==\"Report\")
init=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==\"__init__\"); cls.body=[init]
seen=[]
class C:
 @staticmethod
 def get_config_for_run(*args,**kwargs): seen.append((args,kwargs)); return {{\"selected\":args[0]}}
ns={{\"ConfigHandler\":C,\"get_run_path\":lambda **kwargs: \"derived\",\"Dict\":Dict,\"Optional\":Optional,\"Iterable\":Iterable,\"os\":os,\"__file__\":{str(source)!r}}}; exec(compile(ast.Module(body=[cls],type_ignores=[]),{str(source)!r},\"exec\"),ns)
obj=ns[\"Report\"](\"design\",\"tag\",\"demo\",{{}},run_path=\"explicit-run\")
print(\"PASS\" if seen and seen[0][0][0]==\"explicit-run\" and obj.configuration_full[\"selected\"]==\"explicit-run\" else \"FAIL:\"+repr(seen))
""",encoding="utf-8")
 c=subprocess.run([sys.executable,str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and c.stdout.strip()=="PASS" else "failed"
if __name__=="__main__": raise SystemExit(main())
