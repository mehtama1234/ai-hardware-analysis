#!/usr/bin/env python3
"""Build a bounded decision package from a local multi-module replay."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report_path = args.report.resolve()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    modules = report["model"]["target_modules"]
    hybrid = next(row for row in report["variants"] if row["id"] == "dac10_weight8_adc12")
    quality = hybrid["quality"]
    gates = [
        {"gate": "frozen_multi_module_workload", "passed": len(modules) == 3 and len(report["fixture"]["evaluation"]) == 4},
        {"gate": "per_module_shape_and_tensor_replay", "passed": all(row["output_vector_count"] == 162 for row in hybrid["modules"].values())},
        {"gate": "ideal_multi_module_control", "passed": next(row for row in report["variants"] if row["id"] == "ideal_tiled_control")["exploratory_quality_screen_pass"]},
        {"gate": "joint_adc12_task_quality", "passed": hybrid["exploratory_quality_screen_pass"],
         "detail": f"argmax agreement {quality['teacher_forced_argmax_agreement']:.6f}; generations {quality['generation_exact_match_count']}/{len(report['fixture']['evaluation'])}"},
        {"gate": "disjoint_per_module_calibration", "passed": False, "detail": "not yet run for all three modules"},
        {"gate": "multi_module_runtime_trace_agreement", "passed": False, "detail": "multi-module governed schedule not yet emitted"},
        {"gate": "matched_multi_module_cost", "passed": False, "detail": "only single-module modeled coefficients exist"},
        {"gate": "analog_authorization", "passed": False},
    ]
    result = {
        "schema_version": "gpt2-multimodule-decision-v0.1",
        "result_type": "bounded_local_multi_module_model_to_workload_decision",
        "source_report": {"path": str(report_path), "sha256": digest(report_path)},
        "target_modules": modules,
        "gates": gates,
        "passed_gate_count": sum(row["passed"] for row in gates),
        "gate_count": len(gates),
        "decision": "multi_module_hybrid_benefit_unproven",
        "runtime_decision": "digital_reference_and_deterministic_fallback_only",
        "analog_candidate_authorized": False,
        "claim_boundary": "Local multi-module software replay only. Joint ADC12 quality fails the provisional screen; no calibration, measured runtime, energy, silicon, or analog authorization claim is made.",
    }
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    decision_path = output / "decision_audit.json"
    decision_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    claim_ledger = {
        "schema_version": "gpt2-multimodule-claim-ledger-v0.1",
        "claims": [
            {"claim": "three_module_frozen_replay", "status": "proven_local", "evidence": str(report_path)},
            {"claim": "ideal_control", "status": "proven_local_bounded", "evidence": "ideal_tiled_control"},
            {"claim": "joint_adc12_task_quality", "status": "not_proven", "evidence": "teacher-forced argmax agreement below provisional threshold"},
            {"claim": "per_module_calibration_generalization", "status": "not_run", "evidence": "no multi-module calibration receipt"},
            {"claim": "multi_module_runtime_agreement", "status": "not_run", "evidence": "no governed multi-module runtime trace"},
            {"claim": "matched_cost_or_energy_advantage", "status": "modeled_only_incomplete", "evidence": "no matched multi-module coefficients"},
            {"claim": "analog_execution_authorization", "status": "not_authorized", "evidence": "analog_candidate_authorized=false"},
        ],
        "claim_boundary": result["claim_boundary"],
    }
    claim_path = output / "claim_ledger.json"
    claim_path.write_text(json.dumps(claim_ledger, indent=2) + "\n", encoding="utf-8")
    manifest = {"files": [
        {"path": str(decision_path), "sha256": digest(decision_path)},
        {"path": str(claim_path), "sha256": digest(claim_path)},
        {"path": str(report_path), "sha256": digest(report_path)},
    ]}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (output / "README.md").write_text(
        "# Multi-module local qualification decision\n\n"
        f"The joint ADC12 replay covers {len(modules)} GPT-2 modules and fails the provisional task-quality screen "
        f"at {quality['teacher_forced_argmax_agreement']:.4f} teacher-forced argmax agreement, while preserving "
        f"{quality['generation_exact_match_count']}/{len(report['fixture']['evaluation'])} exact generations.\n\n"
        "This is a bounded negative local result. Per-module calibration, governed runtime tracing, matched cost, "
        "and physical authorization remain open.\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(decision_path), "passed": result["passed_gate_count"],
                      "gates": result["gate_count"], "decision": result["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
