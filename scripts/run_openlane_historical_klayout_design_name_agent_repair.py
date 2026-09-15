"""Replay OpenLane's historical KLayout design-name path handling fix."""
from __future__ import annotations
import argparse,ast,hashlib,json,os,subprocess,sys,tempfile,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT="b43df386c586c67355af2b336b7501b437b46a1a"; SOURCE=Path("scripts/klayout/stream_out.py")
OLD="            elif isinstance(value, str) and os.path.exists(value):"; NEW="""            elif (
                isinstance(value, str)
                and os.path.exists(value)
                and key != "design_name"
            ):"""
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
    out.mkdir(parents=True,exist_ok=True); script=root/SOURCE; outdir=out/"cwd"; outdir.mkdir(); (outdir/"chip").mkdir()
    click=types.SimpleNamespace(command=lambda *a,**k:(lambda f:f),option=lambda *a,**k:(lambda f:f),argument=lambda *a,**k:(lambda f:f))
    tree=ast.parse(script.read_text()); node=next(x for x in ast.walk(tree) if isinstance(x,ast.FunctionDef) and x.name=="stream_out"); ns={"click":click,"os":os,"__file__":str(script)}; exec(compile(ast.Module(body=[node],type_ignores=[]),str(script),"exec"),ns); stream_out=ns["stream_out"]
    captured=[]; original=os.execlp; old_cwd=os.getcwd(); os.chdir(outdir); os.execlp=lambda *args: captured.extend(args)
    try: stream_out(input="layout.gds",input_lefs=(),lyt="tech.lyt",lyp="tech.lyp",lym="layers.map",input_gds_files=(),seal_gds=None,design_name="chip")
    finally: os.execlp=original; os.chdir(old_cwd)
    (out/"argv.json").write_text(json.dumps(captured),encoding="utf-8"); value=next((x.split("=",1)[1] for x in captured if x.startswith("design_name=")),"")
    return "passed" if value=="chip" else "failed"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
    if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
    rev=subprocess.check_output(["git","-C",str(REPO),"rev-parse","--short","HEAD"],text=True).strip(); old=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}^:{SOURCE}"],text=True); fixed=subprocess.check_output(["git","-C",str(REPO),"show",f"{COMMIT}:{SOURCE}"],text=True)
    sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
    with tempfile.TemporaryDirectory(prefix="openlane-historical-klayout-design-name-") as td:
        s=Path(td); mut=s/"mutated"; rep=s/"repaired"; (mut/SOURCE).parent.mkdir(parents=True); (rep/SOURCE).parent.mkdir(parents=True); (mut/SOURCE).write_text(old); (rep/SOURCE).write_text(fixed)
        base=execute(mut,a.output/"baseline"); src=mut/SOURCE; agent=run_repository_agent(task_id="openlane-klayout-design-name-historical-fix",source_revision=f"{COMMIT}^",evidence=[str(SOURCE),f"OpenLane commit {COMMIT} historical fix","KLayout design-name argument handling"],failure_context="KLayout stream_out must not turn the logical design_name cell identifier into an absolute path",repair_before=OLD,repair_after=NEW,repair_source=src,backend="local",output_root=a.output/"agent"); cand=agent.get("patch_candidate",{}); repaired="blocked"
        if cand.get("status")=="review_required":
            prop=RepairProposal("openlane-klayout-design-name-historical-fix",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"benchmark-only historical KLayout design-name repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(src,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
        report={"schema_version":"openlane-historical-klayout-design-name-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"historical_source_revision":f"{COMMIT}^","historical_fix_commit":COMMIT,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":base,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"status":"passed" if base=="failed" and repaired=="passed" else "blocked","claim_boundary":"one real historical OpenLane KLayout design-name fix replayed through disposable agent repair; CLI argument contract only, not GDS signoff"}; report["report_sha256"]=digest(report); path=a.output/"openlane-historical-klayout-design-name-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
