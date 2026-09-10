from __future__ import annotations
import json, hashlib
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))
from verification_platform.repair import RepairProposal, apply_to_copy
from verification_platform.simulation import run_iverilog_vvp
from verification_platform.benchmark_setup import write_planning_artifacts

def main() -> int:
    run = ROOT / "runs" / "retest"; run.mkdir(parents=True, exist_ok=True)
    write_planning_artifacts(ROOT / "spec.md", run, source_revision="seeded-fifo-v1-repair-1")
    proposal = RepairProposal("REQ-FIFO-WRITE", "fifo.sv", 10, "count <= count + 3'd1;", "if (count < DEPTH) count <= count + 3'd1;", "gate writes when FIFO is full")
    repaired = apply_to_copy(ROOT/"fifo.sv", run/"fifo_repaired.sv", proposal, human_approved=True)
    comp, sim = run_iverilog_vvp(repaired, ROOT / "tb.sv", run_root=run, source_revision="seeded-fifo-v1-repair-1", binary_name="fifo.vvp", tool_prefix="fifo-retest")
    original_hash = hashlib.sha256((ROOT/"fifo.sv").read_bytes()).hexdigest()
    repaired_hash = hashlib.sha256(repaired.read_bytes()).hexdigest()
    report = {"schema_version":"seeded-fifo-retest-v1","design":"seeded_fifo","status":"passed" if sim and sim.status == "passed" else "failed","human_approved":True,"repair":{"requirement_id":proposal.requirement_id,"decision":proposal.decision(human_approved=True),"source":"fifo.sv","destination":"runs/retest/fifo_repaired.sv","original_source_sha256":original_hash,"repaired_source_sha256":repaired_hash,"original_unchanged":original_hash == hashlib.sha256((ROOT/"fifo.sv").read_bytes()).hexdigest()},"tool_runs":[comp.__dict__, *([sim.__dict__] if sim else [])]}
    (run/"retest-report.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str)+"\n")
    print(json.dumps(report, sort_keys=True, default=str)); return 0 if report["status"] == "passed" else 1
if __name__ == "__main__": raise SystemExit(main())
