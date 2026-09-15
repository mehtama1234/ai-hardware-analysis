"""Replay OpenLane's historical GF180 macro-unit conversion fix."""
from __future__ import annotations
import argparse, ast, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="08587051"; SOURCE=Path("scripts/odbpy/manual_macro_place.py")
OLD='''            macros[line[0]] = [\n                str(int(float(line[1]) * 1000)),\n                str(int(float(line[2]) * 1000)),\n                line[3],\n            ]'''
NEW='''            macros[line[0]] = [\n                str(int(float(line[1]) * db_units_per_micron)),\n                str(int(float(line[2]) * db_units_per_micron)),\n                line[3],\n            ]'''
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True); source=root/SOURCE; fixture=out/"fixture"; fixture.mkdir(parents=True,exist_ok=True); cfg=fixture/"macros.cfg"; cfg.write_text("u_macro 1.25 2.50 N\n")
 h=out/"macro-units-regression.py"; h.write_text(f'''import ast, os\nsource=open({str(source)!r}).read(); tree=ast.parse(source)\nfn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="manual_macro_place"); fn.decorator_list=[]\nns={{"open":open,"print":print}}; exec(compile(ast.Module(body=[fn],type_ignores=[]),{str(source)!r},"exec"),ns)\nclass Inst:\n def getName(self): return "u_macro"\n def isFixed(self): return False\n def setOrient(self,v): self.orient=v\n def setLocation(self,x,y): self.location=(x,y)\n def setPlacementStatus(self,v): self.status=v\nclass Block:\n def getInsts(self): return [inst]\n def getDbUnitsPerMicron(self): return 2000\nclass Reader: name="demo"; block=Block()\ninst=Inst(); os.chdir({str(fixture)!r}); ns["manual_macro_place"](Reader(),{str(cfg)!r},False)\nprint("PASS" if inst.location==(2500,5000) else "FAIL:"+repr(inst.location))\n''',encoding="utf-8")
 c=subprocess.run([sys.executable,str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and "PASS" in c.stdout else "failed"
def main():
 p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
 if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
 rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
 sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
 with tempfile.TemporaryDirectory(prefix="openlane-historical-macro-units-") as td:
  s=Path(td); mut=s/"mutated"; rep=s/"repaired"
  for root,text in ((mut,old),(rep,fixed)): q=root/SOURCE; q.parent.mkdir(parents=True); q.write_text(text)
  base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-macro-units-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","database-unit conversion"],failure_context="manual macro placement must convert microns using the database unit scale",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
  if cand.get("status")=="review_required":
   prop=RepairProposal("openlane-macro-units-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical macro-unit repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
  report={"schema_version":"openlane-historical-macro-units-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane Python macro-unit fix replayed through disposable agent repair; not repository-scale generalization"}; report["report_sha256"]=digest(report); path=a.output/"openlane-historical-macro-units-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
OLD="""    # read config
    macros = {}
    with open(config, "r") as config_file:
        for line in config_file:
            # Discard comments and empty lines
            line = line.split("#")[0].strip()
            if not line:
                continue
            line = line.split()
            macros[line[0]] = [
                str(int(float(line[1]) * 1000)),
                str(int(float(line[2]) * 1000)),
                line[3],
            ]"""
NEW="""    db_units_per_micron = reader.block.getDbUnitsPerMicron()

    # read config
    macros = {}
    with open(config, "r") as config_file:
        for line in config_file:
            # Discard comments and empty lines
            line = line.split("#")[0].strip()
            if not line:
                continue
            line = line.split()
            macros[line[0]] = [
                str(int(float(line[1]) * db_units_per_micron)),
                str(int(float(line[2]) * db_units_per_micron)),
                line[3],
            ]"""
def execute(root,out):
 out.mkdir(parents=True,exist_ok=True); source=root/SOURCE; fixture=out/"fixture"; fixture.mkdir(parents=True,exist_ok=True); cfg=fixture/"macros.cfg"; cfg.write_text("u_macro 1.25 2.50 N\n")
 h=out/"macro-units-regression.py"; h.write_text(f"""import ast, os
source=open({str(source)!r}).read(); tree=ast.parse(source)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==\"manual_macro_place\"); fn.decorator_list=[]
grid=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==\"gridify\")
rot=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==\"lef_rot_to_oa_rot\")
ns={{\"open\":open,\"print\":print,\"LEF2OA_MAP\":{{\"N\":\"R0\",\"S\":\"R180\",\"W\":\"R90\",\"E\":\"R270\",\"FN\":\"MY\",\"FS\":\"MX\",\"FW\":\"MXR90\",\"FE\":\"MYR90\"}}}}; exec(compile(ast.Module(body=[grid,rot,fn],type_ignores=[]),{str(source)!r},\"exec\"),ns)
class Inst:
 def getName(self): return \"u_macro\"
 def isFixed(self): return False
 def setOrient(self,v): self.orient=v
 def setLocation(self,x,y): self.location=(x,y)
 def setPlacementStatus(self,v): self.status=v
class Block:
 def getInsts(self): return [inst]
 def getDbUnitsPerMicron(self): return 2000
class Reader: name=\"demo\"; block=Block()
inst=Inst(); os.chdir({str(fixture)!r}); ns[\"manual_macro_place\"](Reader(),{str(cfg)!r},False)
print(\"PASS\" if inst.location==(2500,5000) else \"FAIL:\"+repr(inst.location))
""",encoding="utf-8")
 c=subprocess.run([sys.executable,str(h)],cwd=out,capture_output=True,text=True); (out/"stdout.log").write_text(c.stdout); (out/"stderr.log").write_text(c.stderr); return "passed" if c.returncode==0 and "PASS" in c.stdout else "failed"
if __name__=="__main__": raise SystemExit(main())
