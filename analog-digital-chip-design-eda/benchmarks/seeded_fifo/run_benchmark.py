"""Run the seeded FIFO through the open-source simulation evidence contract."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))
from verification_platform.triage import parse_failure, locate_source_marker
from verification_platform.simulation import run_iverilog_vvp
from verification_platform.logic import dependency_cone
from verification_platform.benchmark_setup import write_planning_artifacts


def main() -> int:
    run = ROOT / "runs" / "latest"
    run.mkdir(parents=True, exist_ok=True)
    write_planning_artifacts(ROOT / "spec.md", run, source_revision="seeded-fifo-v1")
    compile_run, sim_run = run_iverilog_vvp(ROOT / "fifo.sv", ROOT / "tb.sv", run_root=run, source_revision="seeded-fifo-v1", binary_name="fifo.vvp", tool_prefix="fifo")
    text = ""
    if sim_run:
        text = (run / "simulation" / "stdout.log").read_text(encoding="utf-8") + (run / "simulation" / "stderr.log").read_text(encoding="utf-8")
    failure = parse_failure(text)
    report = {
        "schema_version": "seeded-fifo-triage-v1",
        "status": "failed" if failure else ("passed" if sim_run and sim_run.status == "passed" else "blocked"),
        "design": "seeded_fifo",
        "source_revision": "seeded-fifo-v1",
        "tool_runs": [compile_run.__dict__, *( [sim_run.__dict__] if sim_run else [])],
        "failure": ({"cycle": failure.cycle, "signal": failure.signal, "expected": failure.expected, "actual": failure.actual} if failure else None),
        "root_cause": ({"file": "fifo.sv", "line": locate_source_marker(ROOT / "fifo.sv", "SEEDED_BUG"), "marker": "SEEDED_BUG", "hypothesis": "write increments count while FIFO is full", "dependency_cone": sorted(dependency_cone(ROOT / "fifo.sv", "count"))} if failure else None),
        "evidence": ["spec.md", "fifo.sv", "tb.sv", "runs/latest/waveform.vcd"],
    }
    (run / "triage-report.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
