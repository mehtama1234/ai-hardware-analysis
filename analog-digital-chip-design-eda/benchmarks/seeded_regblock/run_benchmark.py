"""Run the seeded register-address decode failure."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))
from verification_platform.simulation import run_iverilog_vvp
from verification_platform.triage import parse_failure, locate_source_marker
from verification_platform.logic import dependency_cone
from verification_platform.benchmark_setup import write_planning_artifacts

def main() -> int:
    run = ROOT / "runs" / "latest"; run.mkdir(parents=True, exist_ok=True)
    write_planning_artifacts(ROOT / "spec.md", run, source_revision="seeded-regblock-v1")
    comp, sim = run_iverilog_vvp(ROOT / "regblock.sv", ROOT / "tb.sv", run_root=run, source_revision="seeded-regblock-v1", binary_name="regblock.vvp", tool_prefix="regblock")
    text = "" if sim is None else (run/"simulation"/"stdout.log").read_text() + (run/"simulation"/"stderr.log").read_text()
    failure = parse_failure(text)
    report = {"schema_version":"seeded-regblock-triage-v1", "design":"seeded_regblock", "source_revision":"seeded-regblock-v1", "status":"failed" if failure else ("passed" if sim and sim.status == "passed" else "blocked"), "failure": ({"cycle":failure.cycle,"signal":failure.signal,"expected":failure.expected,"actual":failure.actual} if failure else None), "root_cause": ({"file":"regblock.sv","line":locate_source_marker(ROOT/"regblock.sv", "SEEDED_BUG"),"marker":"SEEDED_BUG","hypothesis":"nonzero address writes update reg0","dependency_cone":sorted(dependency_cone(ROOT/"regblock.sv", "reg0"))} if failure else None), "tool_runs":[comp.__dict__, *([sim.__dict__] if sim else [])], "evidence":["spec.md","regblock.sv","tb.sv","runs/latest/waveform.vcd"]}
    (run/"triage-report.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str)+"\n")
    print(json.dumps(report, sort_keys=True, default=str)); return 0
if __name__ == "__main__": raise SystemExit(main())
