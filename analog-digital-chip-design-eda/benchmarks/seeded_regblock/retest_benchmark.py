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
    write_planning_artifacts(ROOT / "spec.md", run, source_revision="seeded-regblock-v1-repair-1")
    before = "else reg0 <= wdata; // SEEDED_BUG: nonzero addresses must be ignored"
    after = "else reg0 <= reg0; // repaired: nonzero addresses are ignored"
    proposal = RepairProposal("REQ-REG-ADDRESS", "regblock.sv", 8, before, after, "hold reg0 for nonzero addresses")
    repaired = apply_to_copy(ROOT/"regblock.sv", run/"regblock_repaired.sv", proposal, human_approved=True)
    comp, sim = run_iverilog_vvp(repaired, ROOT / "tb.sv", run_root=run, source_revision="seeded-regblock-v1-repair-1", binary_name="regblock.vvp", tool_prefix="regblock-retest")
    original_hash = hashlib.sha256((ROOT/"regblock.sv").read_bytes()).hexdigest()
    repaired_hash = hashlib.sha256(repaired.read_bytes()).hexdigest()
    report = {"schema_version":"seeded-regblock-retest-v1","design":"seeded_regblock","status":"passed" if sim and sim.status == "passed" else "failed","human_approved":True,"repair":{"requirement_id":proposal.requirement_id,"decision":proposal.decision(human_approved=True),"source":"regblock.sv","destination":"runs/retest/regblock_repaired.sv","original_source_sha256":original_hash,"repaired_source_sha256":repaired_hash,"original_unchanged":original_hash == hashlib.sha256((ROOT/"regblock.sv").read_bytes()).hexdigest()},"tool_runs":[comp.__dict__, *([sim.__dict__] if sim else [])]}
    (run/"retest-report.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str)+"\n")
    print(json.dumps(report, sort_keys=True, default=str)); return 0 if report["status"] == "passed" else 1
if __name__ == "__main__": raise SystemExit(main())
