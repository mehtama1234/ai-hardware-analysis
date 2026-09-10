from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent.parent))
from verification_platform.benchmark_setup import write_planning_artifacts
from verification_platform.repair import RepairProposal,apply_to_copy
from verification_platform.simulation import run_iverilog_vvp, run_verilator_lint
from verification_platform.uvm import write_uvm_agent
from verification_platform.rtl import ingest_rtl_ports, write_rtl_inventory
from verification_platform.formal import yosys_syntax_check

def main()->int:
    run=ROOT/"runs"/"retest"; run.mkdir(parents=True,exist_ok=True)
    write_planning_artifacts(ROOT/"spec.md",run,source_revision="register-peripheral-v1-repair-1")
    write_uvm_agent("RegisterPeripheralAgent", ["clk", "rst", "valid", "write", "addr", "wdata", "ready", "control"], run / "uvm-register-peripheral-agent.sv")
    wrapper = ingest_rtl_ports(ROOT / "peripheral.sv", root=ROOT, source_revision="register-peripheral-v1-repair-1")
    regs = ingest_rtl_ports(ROOT / "csr_regs.sv", root=ROOT, source_revision="register-peripheral-v1-repair-1")
    write_rtl_inventory(run / "rtl-collateral.json", {"schema_version": "rtl-collateral-bundle-v1", "modules": wrapper["modules"] + regs["modules"], "sources": [wrapper["source"], regs["source"]]})
    proposal=RepairProposal("REQ-CSR-ADDRESS","csr_regs.sv",4,"else if (wr_en) control <= wdata; // SEEDED_BUG: decode addr zero before write","else if (wr_en && addr == 2'd0) control <= wdata; // repaired address decode","gate CSR writes on address zero")
    repaired=apply_to_copy(ROOT/"csr_regs.sv",run/"csr_regs_repaired.sv",proposal,human_approved=True)
    comp,sim=run_iverilog_vvp(repaired,ROOT/"peripheral.sv",ROOT/"tb.sv",run_root=run,source_revision="register-peripheral-v1-repair-1",binary_name="peripheral.vvp",tool_prefix="register-peripheral-retest")
    formal = yosys_syntax_check(repaired, run_root=run / "formal", top="csr_regs", source_revision="register-peripheral-v1-repair-1")
    lint = run_verilator_lint(repaired, ROOT / "peripheral.sv", run_root=run / "lint", source_revision="register-peripheral-v1-repair-1", top="peripheral")
    original_hash=hashlib.sha256((ROOT/"csr_regs.sv").read_bytes()).hexdigest()
    report={"schema_version":"register-peripheral-retest-v1","design":"register_peripheral","status":"passed" if sim and sim.status=="passed" else "failed","human_approved":True,"repair":{"requirement_id":proposal.requirement_id,"decision":proposal.decision(human_approved=True),"source":"csr_regs.sv","destination":"runs/retest/csr_regs_repaired.sv","original_source_sha256":original_hash,"repaired_source_sha256":hashlib.sha256(repaired.read_bytes()).hexdigest(),"original_unchanged":original_hash==hashlib.sha256((ROOT/"csr_regs.sv").read_bytes()).hexdigest()},"tool_runs":[comp.__dict__,*([sim.__dict__] if sim else []),formal.__dict__,lint.__dict__],"formal_preflight":formal.status,"verilator_lint":lint.status}
    (run/"retest-report.json").write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n"); print(json.dumps(report,sort_keys=True,default=str)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
