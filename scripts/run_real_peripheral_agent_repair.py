"""Replay a behavioral mutation on the real OpenLane peripheral hierarchy."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SUBREPO=ROOT/"analog-digital-chip-design-eda"; REPO=Path(os.environ.get("OPENLANE_REPO_ROOT", "/home/mehtama1/eda-tools/OpenLane"))
DESIGN=Path("designs/peripheral/src"); SOURCE=DESIGN/"csr_regs.sv"; TOP=DESIGN/"peripheral.sv"; TB=Path("benchmarks/register_peripheral/tb.sv")
OLD="    else if (wr_en) control <= wdata; // SEEDED_BUG: decode addr zero before write"
NEW="    else if (wr_en && addr == 2'd0) control <= wdata; // SEEDED_BUG: decode addr zero before write"
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def execute(root,out):
    out.mkdir(parents=True,exist_ok=True); binary=out/"peripheral.vvp"; tb=root/TB; cmd=["iverilog","-g2012","-o",str(binary),str(root/SOURCE),str(root/TOP),str(tb)]
    c=subprocess.run(cmd,capture_output=True,text=True); (out/"compile.stdout.log").write_text(c.stdout); (out/"compile.stderr.log").write_text(c.stderr)
    if c.returncode: return "failed"
    v=subprocess.run(["vvp",str(binary)],capture_output=True,text=True); (out/"simulation.stdout.log").write_text(v.stdout); (out/"simulation.stderr.log").write_text(v.stderr)
    return "passed" if v.returncode==0 and "FAIL " not in v.stdout+v.stderr and "PASS" in v.stdout else "failed"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); p.add_argument("--backend",choices=("mock","local"),default="mock"); p.add_argument("--causal-report",type=Path); a=p.parse_args(); a.output=a.output.resolve(); a.output.mkdir(parents=True,exist_ok=True)
    if a.backend=="mock": os.environ["VERIFICATION_LLM_COMMAND"]=f"{sys.executable} {SUBREPO/'scripts/mock_repository_agent_backend.py'}"
    revision=subprocess.run(["git","-C",str(REPO),"rev-parse","--short","HEAD"],capture_output=True,text=True,check=False); rev=revision.stdout.strip() if revision.returncode==0 and revision.stdout.strip() else "packaged-openlane-four-causal-task-v1"
    fixed=(REPO/SOURCE).read_text(encoding="utf-8")
    sys.path.insert(0,str(SUBREPO)); from verification_platform.repository_agent import run_repository_agent; from verification_platform.repair import RepairProposal,apply_to_copy
    with tempfile.TemporaryDirectory(prefix="real-openlane-peripheral-") as td:
        s=Path(td); mut=s/"mutated"; rep=s/"repaired"
        for root in (mut,rep):
            (root/DESIGN).mkdir(parents=True); (root/TB).parent.mkdir(parents=True); (root/TB).write_text((SUBREPO/TB).read_text()); (root/TOP).write_text((REPO/TOP).read_text()); (root/SOURCE).write_text(fixed if root is rep else fixed.replace(NEW,OLD))
        baseline=execute(mut,a.output/"baseline"); source=mut/SOURCE
        causal=json.loads(a.causal_report.read_text()) if a.causal_report else {}; frontier=causal.get("frontier",{}); causal_context=(f" causal evidence: first divergence is {frontier.get('signal')} at time {frontier.get('time')}; use the digest-bound causal timeline and source-bound locations." if causal else ""); evidence=[str(SOURCE),str(TB),"OpenLane peripheral CSR address decode"]+([str(a.causal_report)] if causal else [])
        agent=run_repository_agent(task_id="real-openlane-peripheral-csr-repair",source_revision=f"{rev}",evidence=evidence,failure_context="an unauthorized write to CSR address one must not change control"+causal_context,repair_before=OLD,repair_after=NEW,repair_source=source,backend="local",output_root=a.output/"agent")
        cand=agent.get("patch_candidate",{}); repaired="blocked"
        if cand.get("status")=="review_required":
            prop=RepairProposal("real-openlane-peripheral-csr-repair",str(cand["source"]),int(cand["line"]),str(cand["before"]),str(cand["after"]),"real OpenLane peripheral address-decode repair",str(cand.get("edit_operator","exact_text_replace"))); apply_to_copy(source,rep/SOURCE,prop,human_approved=True); repaired=execute(rep,a.output/"repaired")
        report={"schema_version":"real-openlane-peripheral-agent-repair-report-v1","repository":"OpenLane","repository_revision":rev,"source_file":str(SOURCE),"backend":a.backend,"baseline_status":baseline,"agent_status":agent["team"]["status"],"patch_candidate_status":cand.get("status",agent.get("patch_candidate_status")),"repaired_status":repaired,"canonical_unchanged":True,"causal_report":str(a.causal_report.resolve()) if a.causal_report else None,"causal_report_sha256":hashlib.sha256(a.causal_report.read_bytes()).hexdigest() if a.causal_report else None,"causal_frontier":frontier if causal else None,"status":"passed" if baseline=="failed" and repaired=="passed" else "blocked","claim_boundary":"real OpenLane two-module peripheral behavioral mutation and disposable agent repair; optional digest-bound causal evidence; one CSR protocol invariant, not full design closure"}; report["report_sha256"]=digest(report); path=a.output/"real-openlane-peripheral-agent-repair-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
