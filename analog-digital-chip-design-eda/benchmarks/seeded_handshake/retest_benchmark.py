from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent.parent))
from verification_platform.benchmark_setup import write_planning_artifacts
from verification_platform.repair import RepairProposal,apply_to_copy
from verification_platform.simulation import run_iverilog_vvp
def main()->int:
    run=ROOT/"runs"/"retest"; run.mkdir(parents=True,exist_ok=True); write_planning_artifacts(ROOT/"spec.md",run,source_revision="seeded-handshake-v1-repair-1")
    proposal=RepairProposal("REQ-HS-RESET","handshake.sv",2,"assign ready = 1'b1; // SEEDED_BUG: ready must be low during reset","assign ready = !rst; // repaired reset gating","gate ready with reset")
    repaired=apply_to_copy(ROOT/"handshake.sv",run/"handshake_repaired.sv",proposal,human_approved=True)
    comp,sim=run_iverilog_vvp(repaired,ROOT/"tb.sv",run_root=run,source_revision="seeded-handshake-v1-repair-1",binary_name="handshake.vvp",tool_prefix="handshake-retest")
    original_hash=hashlib.sha256((ROOT/"handshake.sv").read_bytes()).hexdigest()
    report={"schema_version":"seeded-handshake-retest-v1","design":"seeded_handshake","status":"passed" if sim and sim.status=="passed" else "failed","repair":{"requirement_id":proposal.requirement_id,"decision":proposal.decision(human_approved=True),"original_source_sha256":original_hash,"repaired_source_sha256":hashlib.sha256(repaired.read_bytes()).hexdigest(),"original_unchanged":original_hash==hashlib.sha256((ROOT/"handshake.sv").read_bytes()).hexdigest()},"tool_runs":[comp.__dict__,*([sim.__dict__] if sim else [])]}
    (run/"retest-report.json").write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n"); print(json.dumps(report,sort_keys=True,default=str)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
