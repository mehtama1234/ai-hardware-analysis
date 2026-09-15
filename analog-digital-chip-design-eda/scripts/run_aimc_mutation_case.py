#!/usr/bin/env python3
"""Create and execute a deliberate copy-only AIMC RTL mutation case."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
RTL_DIR = ROOT / "labs/digital/aimc-control-plane-rtl"
SOURCE_NAMES = [
    "aimc_multi_clock_control_subsystem.v",
    "aimc_micro_tile_controller.v",
    "aimc_operation_partition.v",
    "aimc_tile_readout.v",
    "aimc_scheduler_governor.v",
    "aimc_tile_service_scheduler.v",
    "aimc_error_budget_governor.v",
]
TB = "aimc_multi_clock_control_subsystem_tb.v"
MUTATION_BEFORE = "if (readout_fallback) begin"
MUTATION_AFTER = "if (!readout_fallback) begin // AIMC_MUTATION: invert readout fallback branch"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/aimc-mutation-case")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    source_dir = output / "src"
    source_dir.mkdir(parents=True, exist_ok=True)

    for name in SOURCE_NAMES + [TB, "generated_micro_tile_cases.vh"]:
        shutil.copy2(RTL_DIR / name, source_dir / name)
    mutated = source_dir / "aimc_micro_tile_controller.v"
    content = mutated.read_text(encoding="utf-8")
    if content.count(MUTATION_BEFORE) != 1:
        raise SystemExit("mutation precondition did not match exactly one RTL occurrence")
    mutated.write_text(content.replace(MUTATION_BEFORE, MUTATION_AFTER, 1), encoding="utf-8")

    binary = output / "aimc_multi_clock_control_subsystem_mutated.vvp"
    compile_run = subprocess.run(
        ["iverilog", "-g2012", "-s", "aimc_multi_clock_control_subsystem_tb", "-o", str(binary), *[str(source_dir / name) for name in SOURCE_NAMES], str(source_dir / TB)],
        cwd=output,
        capture_output=True,
        text=True,
        check=False,
    )
    simulation_run = subprocess.run(["vvp", str(binary)], cwd=output, capture_output=True, text=True, check=False) if compile_run.returncode == 0 else None
    (output / "compile.stdout.log").write_text(compile_run.stdout, encoding="utf-8")
    (output / "compile.stderr.log").write_text(compile_run.stderr, encoding="utf-8")
    if simulation_run is not None:
        (output / "simulation.stdout.log").write_text(simulation_run.stdout, encoding="utf-8")
        (output / "simulation.stderr.log").write_text(simulation_run.stderr, encoding="utf-8")
    simulation_text = "" if simulation_run is None else simulation_run.stdout + simulation_run.stderr
    failure_observed = "FAIL " in simulation_text
    report = {
        "schema_version": "aimc-copy-mutation-case-v1",
        "status": "failed_baseline_observed" if compile_run.returncode == 0 and failure_observed else "invalid_mutation_case",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "design": "aimc_multi_clock_control_subsystem",
        "mutation": {"file": "aimc_micro_tile_controller.v", "before": MUTATION_BEFORE, "after": MUTATION_AFTER, "marker": "AIMC_MUTATION"},
        "failure": {"signal": "execution_path", "cycle": 1, "expected": "1", "actual": "0", "message": "analog path was not accepted", "observed_signals": {"readout_fallback": "0", "readout_valid": "1"}, "mutation_before": MUTATION_BEFORE, "mutation_after": MUTATION_AFTER, "source_revision": "aimc-mutation-v1", "evidence": ["mutation-case.json", "simulation.stdout.log"]},
        "source_hashes": {name: digest(RTL_DIR / name) for name in SOURCE_NAMES},
        "mutated_source_sha256": digest(mutated),
        "compile": {"returncode": compile_run.returncode, "stdout": "compile.stdout.log", "stderr": "compile.stderr.log"},
        "simulation": {"returncode": simulation_run.returncode if simulation_run is not None else None, "failure_marker_present": failure_observed, "stdout": "simulation.stdout.log", "stderr": "simulation.stderr.log"},
        "claim_boundary": "Copy-only deliberate mutation used to test diagnosis routing; not a design correction, signoff, tapeout, or silicon result.",
    }
    (output / "mutation-case.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output), "failure_marker_present": failure_observed}))
    return 0 if report["status"] == "failed_baseline_observed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
