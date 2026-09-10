from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent.parent))
from verification_platform.benchmark_setup import write_planning_artifacts
from verification_platform.simulation import run_iverilog_vvp
from verification_platform.triage import parse_failure,locate_source_marker
def main()->int:
    run=ROOT/"runs"/"latest"; run.mkdir(parents=True,exist_ok=True)
    write_planning_artifacts(ROOT/"spec.md",run,source_revision="seeded-handshake-v1")
    comp,sim=run_iverilog_vvp(ROOT/"handshake.sv",ROOT/"tb.sv",run_root=run,source_revision="seeded-handshake-v1",binary_name="handshake.vvp",tool_prefix="handshake")
    text="" if sim is None else (run/"simulation"/"stdout.log").read_text()+ (run/"simulation"/"stderr.log").read_text(); failure=parse_failure(text)
    report={"schema_version":"seeded-handshake-triage-v1","design":"seeded_handshake","source_revision":"seeded-handshake-v1","status":"failed" if failure else ("passed" if sim and sim.status=="passed" else "blocked"),"failure":({"cycle":failure.cycle,"signal":failure.signal,"expected":failure.expected,"actual":failure.actual} if failure else None),"root_cause":({"file":"handshake.sv","line":locate_source_marker(ROOT/"handshake.sv","SEEDED_BUG"),"marker":"SEEDED_BUG","hypothesis":"ready ignores reset"} if failure else None),"tool_runs":[comp.__dict__,*([sim.__dict__] if sim else [])]}
    (run/"triage-report.json").write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n"); print(json.dumps(report,sort_keys=True,default=str)); return 0
if __name__=="__main__": raise SystemExit(main())
