#!/usr/bin/env python3
"""Repair a deliberate AIMC mutation in a copy and revalidate its RTL inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RTL_DIR = ROOT / "labs/digital/aimc-control-plane-rtl"
PREP_DIR = ROOT / "labs/eda/aimc-multi-clock-control-subsystem-openlane-prep"
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-report", type=Path, required=True)
    parser.add_argument("--mutation-case", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/aimc-mutation-repair-retest")
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--allow-known-reversal", action="store_true", help="Use the fixture's known mutation reversal when no acceptable model repair exists")
    parser.add_argument("--reviewer")
    parser.add_argument("--approval-note")
    args = parser.parse_args()
    model_report = args.model_report.resolve()
    mutation_case_path = args.mutation_case.resolve()
    output = args.output.resolve()
    model = load(model_report)
    mutation = load(mutation_case_path)
    aimc = model.get("aimc_mutation_run")
    if not isinstance(aimc, dict) or not (aimc.get("status") == "available" and aimc.get("grounded") is True and aimc.get("diagnosis_match") is True and aimc.get("adversarial_review", {}).get("accepted") is True):
        raise SystemExit("AIMC model diagnosis is not accepted")
    if mutation.get("status") != "failed_baseline_observed":
        raise SystemExit("mutation case does not prove a failed baseline")
    model_repair = model.get("aimc_mutation_repair_run")
    model_repair_match = isinstance(model_repair, dict) and model_repair.get("status") == "available" and model_repair.get("before") == mutation["failure"]["mutation_after"] and model_repair.get("after") == mutation["failure"]["mutation_before"]
    if (not isinstance(model_repair, dict) or model_repair.get("status") != "available") and not args.allow_known_reversal:
        print(json.dumps({"status": "review_required", "reason": "the model did not emit a valid structured repair proposal", "model_report": str(model_report), "model_repair": model_repair}, sort_keys=True))
        return 0
    if isinstance(model_repair, dict) and model_repair.get("status") == "available" and (model_repair.get("grounded") is not True or not model_repair_match) and not args.allow_known_reversal:
        raise SystemExit("model repair is not grounded or does not exactly reverse the bounded mutation")
    repair_proposal = model_repair.get("proposal") if isinstance(model_repair, dict) else None
    repair_file = repair_proposal.get("file", mutation["mutation"]["file"]) if isinstance(repair_proposal, dict) else mutation["mutation"]["file"]
    if repair_file != mutation["mutation"]["file"]:
        raise SystemExit("model repair targets a file outside the bounded mutation")
    if not args.approve:
        print(json.dumps({"status": "review_required", "reason": "explicit approval is required before applying the copy-only repair"}))
        return 0
    if not args.reviewer or not args.approval_note:
        raise SystemExit("--approve requires --reviewer and --approval-note")

    mutation_dir = mutation_case_path.parent / "src"
    if not mutation_dir.is_dir():
        raise SystemExit("mutation source directory is missing; retain the mutation package before retest")
    output.mkdir(parents=True, exist_ok=True)
    repaired_src = output / "src"
    repaired_src.mkdir(parents=True, exist_ok=True)
    for name in SOURCE_NAMES + [TB, "generated_micro_tile_cases.vh"]:
        shutil.copy2(mutation_dir / name, repaired_src / name)
    target = repaired_src / "aimc_micro_tile_controller.v"
    content = target.read_text(encoding="utf-8")
    proposed_before = model_repair.get("before") if model_repair_match else mutation["mutation"]["after"]
    proposed_after = model_repair.get("after") if model_repair_match else mutation["mutation"]["before"]
    if not isinstance(proposed_before, str) or not isinstance(proposed_after, str):
        raise SystemExit("model repair is missing exact before/after RTL text")
    if content.count(proposed_before) != 1:
        raise SystemExit("repair precondition did not match exactly one mutation")
    target.write_text(content.replace(proposed_before, proposed_after, 1), encoding="utf-8")

    binary = output / "aimc_multi_clock_control_subsystem_repaired.vvp"
    compile_run = subprocess.run(["iverilog", "-g2012", "-s", "aimc_multi_clock_control_subsystem_tb", "-o", str(binary), *[str(repaired_src / name) for name in SOURCE_NAMES], str(repaired_src / TB)], cwd=output, capture_output=True, text=True, check=False)
    simulation_run = subprocess.run(["vvp", str(binary)], cwd=output, capture_output=True, text=True, check=False) if compile_run.returncode == 0 else None
    (output / "compile.stdout.log").write_text(compile_run.stdout, encoding="utf-8")
    (output / "compile.stderr.log").write_text(compile_run.stderr, encoding="utf-8")
    if simulation_run is not None:
        (output / "simulation.stdout.log").write_text(simulation_run.stdout, encoding="utf-8")
        (output / "simulation.stderr.log").write_text(simulation_run.stderr, encoding="utf-8")
    source_alignment = {name: {"repaired_sha256": digest(repaired_src / name), "canonical_sha256": digest(RTL_DIR / name), "physical_input_sha256": digest(PREP_DIR / "src" / name), "canonical_match": digest(repaired_src / name) == digest(RTL_DIR / name), "physical_input_match": digest(repaired_src / name) == digest(PREP_DIR / "src" / name)} for name in SOURCE_NAMES}
    passed = compile_run.returncode == 0 and simulation_run is not None and simulation_run.returncode == 0 and "PASS aimc_multi_clock_control_subsystem_tb" in simulation_run.stdout and all(item["canonical_match"] and item["physical_input_match"] for item in source_alignment.values())
    model_generated = model_repair_match
    report = {"schema_version": "aimc-mutation-repair-retest-v2", "status": "passed" if passed else "failed", "generated_at": datetime.now(timezone.utc).isoformat(), "design": "aimc_multi_clock_control_subsystem", "approval": {"status": "approved", "reviewer": args.reviewer, "note": args.approval_note}, "model_report_sha256": digest(model_report), "mutation_case_sha256": digest(mutation_case_path), "repair": {"file": repair_file, "before": proposed_before, "after": proposed_after, "model_generated": model_generated, "known_bounded_mutation_reversal": not model_generated}, "compile": {"returncode": compile_run.returncode}, "simulation": {"returncode": simulation_run.returncode if simulation_run is not None else None, "pass_marker_present": bool(simulation_run is not None and "PASS aimc_multi_clock_control_subsystem_tb" in simulation_run.stdout)}, "source_alignment": source_alignment, "physical_revalidation": {"status": "passed" if all(item["physical_input_match"] for item in source_alignment.values()) else "failed", "package": str(PREP_DIR.relative_to(ROOT))}, "claim_boundary": "A bounded repair applied only in a disposable copy after explicit approval; model-generated status is true only when the model's exact before/after text matches the mutation. Mechanical RTL and physical-input revalidation only. Not commercial signoff, tapeout, or silicon evidence."}
    (output / "repair-retest.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output), "physical_revalidation": report["physical_revalidation"]["status"]}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
