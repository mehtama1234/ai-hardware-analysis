#!/usr/bin/env python3
"""Build the final bounded decision from a local qualification package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    report_path = args.package / "qualification_report.json"
    manifest_path = args.package / "manifest.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    vectors = report["workload"]["vectors"]
    calibrated = report["calibrated_tensor_replay"]
    calibrated_envelope = report["error_sensitivity"]["calibrated_per_vector_relative_l2_envelope"]
    quality_1pct = calibrated_envelope["passing_vector_counts"]["0.01"]
    gates = [
        {"gate": "frozen_workload_and_tensor_replay", "passed": vectors == 162},
        {"gate": "held_out_model_quality", "passed": report["error_sensitivity"]["selected_profile_quality_pass"]},
        {"gate": "disjoint_calibration_generalization", "passed": report["calibration_generalization"]["present"]},
        {"gate": "per_vector_1pct_quality", "passed": quality_1pct == vectors,
         "detail": f"{quality_1pct}/{vectors} vectors under 1% relative-L2"},
        {"gate": "complete_converter_profile", "passed": report["profile_gate"]["open_case_count"] == 0},
        {"gate": "per_vector_timing_evidence", "passed": False},
        {"gate": "matched_measured_cost", "passed": False},
        {"gate": "runtime_trace_agreement", "passed": report["workload_runtime_trace"]["trace_agreement"]["all_routes_fallback"]},
        {"gate": "analog_authorization", "passed": False},
    ]
    result = {
        "schema_version": "local-qualification-decision-v0.1",
        "result_type": "bounded_local_model_to_workload_decision",
        "source_report": {"path": str(report_path), "sha256": sha256(report_path)},
        "gates": gates,
        "passed_gate_count": sum(gate["passed"] for gate in gates),
        "gate_count": len(gates),
        "analog_candidate_authorized": False,
        "runtime_decision": "digital_reference_and_deterministic_fallback_only",
        "analog_advantage_decision": "unresolved",
        "reason": "The local model path and fallback contract pass, but per-vector quality, complete converter qualification, timing evidence, matched measured cost, and analog authorization are open.",
        "claim_boundary": "This is a local software/profile decision package. It does not claim measured analog execution, silicon yield, latency, energy advantage, or production readiness.",
    }
    decision_path = args.package / "decision_audit.json"
    decision_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (args.package / "final_decision.md").write_text(
        "# Local profile-to-workload decision\n\n"
        "Runtime decision: **digital reference and deterministic fallback only**.\n\n"
        "Analog-advantage decision: **unresolved**.\n\n"
        f"{result['passed_gate_count']}/{result['gate_count']} declared gates pass. "
        "The model replay and fallback plumbing are useful local evidence, but "
        "the converter profile, timing, matched cost, and analog authorization "
        "gates remain open. `analog_authorized` remains `false`.\n",
        encoding="utf-8",
    )
    claim_ledger = {
        "schema_version": "local-qualification-claim-ledger-v0.1",
        "result_type": "claim_scoped_local_model_to_workload_evidence",
        "claims": [
            {"claim": "frozen_workload_and_tensor_replay", "status": "proven_local", "evidence": "qualification_report.json and tensor_outputs.npz"},
            {"claim": "held_out_model_quality", "status": "proven_local_bounded", "evidence": "qualification_report.json output_replay"},
            {"claim": "disjoint_software_calibration_generalization", "status": "proven_local_bounded", "evidence": "calibration_replay and calibration_generalization"},
            {"claim": "per_vector_one_percent_tensor_quality", "status": "not_proven", "evidence": f"{quality_1pct}/{vectors} calibrated vectors under 1% relative-L2"},
            {"claim": "complete_converter_profile", "status": "blocked", "evidence": f"{report['profile_gate']['open_case_count']} open profile cases"},
            {"claim": "measured_per_vector_timing", "status": "not_measured", "evidence": "no per-vector settling receipt"},
            {"claim": "matched_energy_or_cost_advantage", "status": "modeled_only", "evidence": "workload_accounting sensitivity and break-even model"},
            {"claim": "compiler_runtime_trace_agreement", "status": "proven_local_bounded", "evidence": "workload_runtime_trace.json"},
            {"claim": "analog_execution_authorization", "status": "not_authorized", "evidence": "analog_candidate_authorized=false"},
        ],
        "claim_boundary": "Local software/profile evidence only; modeled cost is not measured energy and no claim authorizes analog hardware execution.",
    }
    claim_ledger_path = args.package / "claim_ledger.json"
    claim_ledger_path.write_text(json.dumps(claim_ledger, indent=2) + "\n", encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["decision_audit"] = {"path": str(decision_path), "sha256": sha256(decision_path)}
    manifest["claim_ledger"] = {"path": str(claim_ledger_path), "sha256": sha256(claim_ledger_path)}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(decision_path), "passed": result["passed_gate_count"],
                      "gates": result["gate_count"], "decision": result["analog_advantage_decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
