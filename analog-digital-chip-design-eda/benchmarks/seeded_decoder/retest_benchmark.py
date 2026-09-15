from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent.parent))
from verification_platform.benchmark_setup import write_planning_artifacts
from verification_platform.repair import RepairProposal,apply_to_copy
from verification_platform.simulation import run_iverilog_vvp
def main()->int:
    run=ROOT/"runs"/"retest"; run.mkdir(parents=True,exist_ok=True); write_planning_artifacts(ROOT/"spec.md",run,source_revision="seeded-decoder-v1-repair-1")
    proposal=RepairProposal("REQ-DEC-OPCODE-2","decoder.sv",8,"        2'd3: decode = 4'b1000;","        2'd2: decode = 4'b0100;\n        2'd3: decode = 4'b1000;","restore the missing opcode branch")
    repaired=apply_to_copy(ROOT/"decoder.sv",run/"decoder_repaired.sv",proposal,human_approved=True)
    comp,sim=run_iverilog_vvp(repaired,ROOT/"tb.sv",run_root=run,source_revision="seeded-decoder-v1-repair-1",binary_name="decoder.vvp",tool_prefix="decoder-retest")
    original_hash=hashlib.sha256((ROOT/"decoder.sv").read_bytes()).hexdigest()
    report={"schema_version":"seeded-decoder-retest-v1","design":"seeded_decoder","status":"passed" if sim and sim.status=="passed" else "failed","repair":{"requirement_id":proposal.requirement_id,"decision":proposal.decision(human_approved=True),"original_source_sha256":original_hash,"repaired_source_sha256":hashlib.sha256(repaired.read_bytes()).hexdigest(),"original_unchanged":original_hash==hashlib.sha256((ROOT/"decoder.sv").read_bytes()).hexdigest()},"tool_runs":[comp.__dict__,*([sim.__dict__] if sim else [])]}
    (run/"retest-report.json").write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n"); print(json.dumps(report,sort_keys=True,default=str)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
