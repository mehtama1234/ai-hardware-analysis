"""Run the hierarchical register-peripheral benchmark."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent.parent))
from verification_platform.benchmark_setup import write_planning_artifacts
from verification_platform.simulation import run_iverilog_vvp, run_verilator_lint
from verification_platform.triage import parse_failure, locate_source_marker
from verification_platform.logic import dependency_cone
from verification_platform.uvm import write_uvm_agent
from verification_platform.rtl import ingest_rtl_ports, write_rtl_inventory
from verification_platform.formal import yosys_syntax_check

def main()->int:
    run=ROOT/"runs"/"latest"; run.mkdir(parents=True,exist_ok=True)
    write_planning_artifacts(ROOT/"spec.md",run,source_revision="register-peripheral-v1")
    write_uvm_agent("RegisterPeripheralAgent", ["clk", "rst", "valid", "write", "addr", "wdata", "ready", "control"], run / "uvm-register-peripheral-agent.sv")
    wrapper = ingest_rtl_ports(ROOT / "peripheral.sv", root=ROOT, source_revision="register-peripheral-v1")
    regs = ingest_rtl_ports(ROOT / "csr_regs.sv", root=ROOT, source_revision="register-peripheral-v1")
    write_rtl_inventory(run / "rtl-collateral.json", {"schema_version": "rtl-collateral-bundle-v1", "modules": wrapper["modules"] + regs["modules"], "sources": [wrapper["source"], regs["source"]]})
    comp,sim=run_iverilog_vvp(ROOT/"csr_regs.sv",ROOT/"peripheral.sv",ROOT/"tb.sv",run_root=run,source_revision="register-peripheral-v1",binary_name="peripheral.vvp",tool_prefix="register-peripheral")
    formal = yosys_syntax_check(ROOT / "csr_regs.sv", run_root=run / "formal", top="csr_regs", source_revision="register-peripheral-v1")
    lint = run_verilator_lint(ROOT / "csr_regs.sv", ROOT / "peripheral.sv", run_root=run / "lint", source_revision="register-peripheral-v1", top="peripheral")
    text="" if sim is None else (run/"simulation"/"stdout.log").read_text()+ (run/"simulation"/"stderr.log").read_text()
    failure=parse_failure(text)
    report={"schema_version":"register-peripheral-triage-v1","design":"register_peripheral","source_revision":"register-peripheral-v1","status":"failed" if failure else ("passed" if sim and sim.status=="passed" else "blocked"),"failure":({"cycle":failure.cycle,"signal":failure.signal,"expected":failure.expected,"actual":failure.actual} if failure else None),"root_cause":({"file":"csr_regs.sv","line":locate_source_marker(ROOT/"csr_regs.sv","SEEDED_BUG"),"marker":"SEEDED_BUG","hypothesis":"nonzero bus address updates control","dependency_cone":sorted(dependency_cone(ROOT/"csr_regs.sv","control"))} if failure else None),"tool_runs":[comp.__dict__,*([sim.__dict__] if sim else []),formal.__dict__,lint.__dict__],"formal_preflight":formal.status,"verilator_lint":lint.status,"evidence":["spec.md","csr_regs.sv","peripheral.sv","tb.sv","runs/latest/waveform.vcd"]}
    (run/"triage-report.json").write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n")
    print(json.dumps(report,sort_keys=True,default=str)); return 0
if __name__=="__main__": raise SystemExit(main())
