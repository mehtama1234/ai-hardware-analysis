#!/usr/bin/env python3
"""Build a hash-bound, fail-closed manifest for the model-to-chip handoff."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


PRODUCT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = PRODUCT_ROOT.parent
DEEPSEEK = WORKSPACE / "DeepSeek-From-Scratch"
EDA = PRODUCT_ROOT / "analog-digital-chip-design-eda"
LOCAL_QUAL = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
              "software-architecture/experiments/gpt2-hybrid-v1/qualification" /
              "local-profile-to-workload-qualification")
MULTI_QUAL = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
              "software-architecture/experiments/gpt2-hybrid-v1/qualification" /
              "local-multimodule-qualification-v2")
MULTI_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
             "software-architecture/experiments/gpt2-hybrid-v1/runs" /
             "20260911-local-multimodule-v2")
SENSITIVITY_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                   "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                   "20260911-local-multimodule-sensitivity-v2")
POLICY_QUAL = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
               "software-architecture/experiments/gpt2-hybrid-v1/qualification" /
               "local-multimodule-fallback-policy-v1")
ATTRIBUTION_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                   "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                   "20260911-local-multimodule-error-attribution-v1")
GOVERNOR_QUAL = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                 "software-architecture/experiments/gpt2-hybrid-v1/qualification" /
                 "local-multimodule-profile-governor-v5")
STRESS_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
              "software-architecture/experiments/gpt2-hybrid-v1/runs" /
              "20260911-local-governor-stress-v3")
CALIBRATION_FIXTURE = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                       "software-architecture/experiments/gpt2-hybrid-v1/fixture-multimodule-calibration-v2.json")
ERROR_BUDGET_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                    "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                    "20260911-local-error-budget-v1")
PROFILE_SWEEP_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                     "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                     "20260911-local-profile-design-sweep-v1")
PROFILE_STRESS_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                      "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                      "20260911-local-profile-design-stress-v1")
RANGE_STRESS_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                    "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                    "20260911-local-profile-attn125-stress-v1")
TRANSFER_SWEEP_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                      "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                      "20260911-local-transfer-model-sweep-v1")
CONTEXT_TRANSFER_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                        "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                        "20260911-local-context-transfer-v1")
STATEFUL_GOVERNOR_QUAL = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                          "software-architecture/experiments/gpt2-hybrid-v1/qualification" /
                          "local-stateful-profile-governor-v1")
MULTICONTEXT_QUAL = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                     "software-architecture/experiments/gpt2-hybrid-v1/qualification" /
                     "local-multicontext-matrix-v1")
STATEFUL_DECISION_QUAL = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                          "software-architecture/experiments/gpt2-hybrid-v1/qualification" /
                          "local-stateful-multimodule-decision-v1")
THIRD_HOLDOUT_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                     "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                     "20260911-local-stateful-third-holdout-v1")
BOUNDARY_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                "20260911-local-boundary-interventions-v1")
ACTIVATION_COVERAGE_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                           "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                           "20260911-local-activation-coverage-v1")
CALIBRATION_V3_FIXTURE = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                          "software-architecture/experiments/gpt2-hybrid-v1/fixture-multimodule-calibration-v3.json")
CALIBRATION_V3_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                      "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                      "20260911-local-stateful-calibration-v3-v1")
SECOND_ORDER_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                    "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                    "20260911-local-second-order-stateful-v1")
INPUT_ENERGY_RESIDUAL_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                             "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                             "20260911-local-input-energy-residual-v1")
MODULE_ERROR_DECOMPOSITION_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                                   "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                                   "20260911-local-module-error-decomposition-v1")
TARGETED_CPROJ_ADC_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                           "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                           "20260911-local-targeted-cproj-adc-v1")
TARGETED_CPROJ_TRANSFER_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                               "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                               "20260911-local-targeted-cproj-transfer-v1")
CPROJ_SETTLING_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                      "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                      "20260911-local-cproj-settling-sweep-v1")
CPROJ_STATE_MACHINE_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                           "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                           "20260911-local-cproj-state-machine-v1")
CIRCUIT_TRANSFER_TABLE_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                              "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                              "20260912-local-circuit-transfer-table-v1")
TRANSFER_TABLE_POLICY_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                             "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                             "20260912-local-transfer-table-fallback-policy-v1")
TRANSFER_TABLE_RUNTIME_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                              "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                              "20260912-local-transfer-table-runtime-trace-v1")
TRANSFORMER_TRANSFER_RUNTIME_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                                    "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                                    "20260912-local-transformer-transfer-table-runtime-v1")
TRANSFORMER_FALLBACK_AUDIT_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                                  "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                                  "20260912-local-transformer-fallback-output-audit-v1")
TRANSFORMER_FINGERPRINT_RUN = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                               "software-architecture/experiments/gpt2-hybrid-v1/runs" /
                               "20260912-local-transformer-per-vector-fallback-fingerprint-v7")
COVERAGE_AWARE_GOVERNOR_QUAL = (PRODUCT_ROOT / "analog-in-memory-ai-inference" /
                                "software-architecture/experiments/gpt2-hybrid-v1/qualification" /
                                "local-coverage-aware-profile-governor-v4")
OUT = PRODUCT_ROOT / "evidence" / "end-to-end-qualification-manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {"path": str(path.relative_to(WORKSPACE)), "present": "false"}
    return {"path": str(path.relative_to(WORKSPACE)), "present": "true", "sha256": digest(path)}


def main() -> int:
    receipt_path = DEEPSEEK / "integration" / "colab-cuda-run-receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else {}
    artifact_checks = []
    for item in receipt.get("artifacts", []):
        path = DEEPSEEK / "integration" / "artifacts" / item["artifact"]
        actual = digest(path) if path.is_file() else None
        artifact_checks.append({
            "artifact": item["artifact"],
            "receipt_sha256": item.get("sha256"),
            "actual_sha256": actual,
            "hash_matches": actual == item.get("sha256"),
            "device": item.get("device"),
            "cuda_name": item.get("cuda_name"),
            "claim_status": item.get("claim_status"),
        })
    gpu_ready = (
        receipt.get("device") == "cuda"
        and bool(receipt.get("cuda_name"))
        and bool(artifact_checks)
        and all(item["hash_matches"] for item in artifact_checks)
        and all(item["claim_status"] == "measured" for item in artifact_checks)
    )
    if not receipt:
        gpu_status = "receipt_missing"
    elif receipt.get("device") != "cuda" or not receipt.get("cuda_name"):
        gpu_status = "receipt_not_cuda"
    elif any(not item["hash_matches"] for item in artifact_checks):
        gpu_status = "receipt_artifact_hash_mismatch"
    elif any(item["claim_status"] != "measured" for item in artifact_checks):
        gpu_status = "artifact_claim_not_measured"
    else:
        gpu_status = "ready"

    profile_path = EDA / "evidence" / "aimc-simulator-adapters" / "sky130-converter-qualification-profile.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    hybrid_path = DEEPSEEK / "integration" / "artifacts" / "uploaded-deep-transformer-mlp-stack-bridge.json"
    model_path = DEEPSEEK / "integration" / "artifacts" / "model-manifest.json"
    physical_sweep = EDA / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-dac-active-hold-sweep.json"
    physical_campaign = EDA / "evidence" / "aimc-simulator-adapters" / "local-fourbit-79ns-50ps-activehold45w4-full.json"
    one_bit_cell = EDA / "evidence" / "aimc-simulator-adapters" / "local-onebit-boundededges-09v-vdd-20260911.json"
    isolated_cell = EDA / "evidence" / "aimc-simulator-adapters" / "sky130-isolated-pmos-r100-180s-bottom-plate-cell.json"
    isolated_long = EDA / "evidence" / "aimc-simulator-adapters" / "sky130-isolated-pmos-r100-long-acquisition.json"
    isolated_reservoir = EDA / "evidence" / "aimc-simulator-adapters" / "sky130-isolated-pmos-r100-rail10p-earlyprecharge.json"
    physical = json.loads(physical_sweep.read_text(encoding="utf-8")) if physical_sweep.is_file() else {}
    local_decision_path = LOCAL_QUAL / "decision_audit.json"
    local_claim_ledger_path = LOCAL_QUAL / "claim_ledger.json"
    local_report_path = LOCAL_QUAL / "qualification_report.json"
    local_decision = json.loads(local_decision_path.read_text(encoding="utf-8")) if local_decision_path.is_file() else {}
    multi_report_path = MULTI_RUN / "multimodule_evaluation.json"
    multi_decision_path = MULTI_QUAL / "decision_audit.json"
    multi_claim_ledger_path = MULTI_QUAL / "claim_ledger.json"
    multi_runtime_path = MULTI_QUAL / "multimodule_runtime_trace.json"
    multi_cost_path = MULTI_QUAL / "multimodule_cost_trace.jsonl"
    sensitivity_report_path = SENSITIVITY_RUN / "sensitivity_report.json"
    error_budget_path = ERROR_BUDGET_RUN / "error_budget_report.json"
    profile_sweep_path = PROFILE_SWEEP_RUN / "profile_design_sweep_report.json"
    profile_stress_path = PROFILE_STRESS_RUN / "stress_validation_report.json"
    range_stress_path = RANGE_STRESS_RUN / "stress_validation_report.json"
    transfer_sweep_path = TRANSFER_SWEEP_RUN / "transfer_model_sweep_report.json"
    context_transfer_path = CONTEXT_TRANSFER_RUN / "context_transfer_report.json"
    stateful_governor_path = STATEFUL_GOVERNOR_QUAL / "stateful_profile_governor.json"
    stateful_cost_path = STATEFUL_GOVERNOR_QUAL / "stateful_route_cost_trace.jsonl"
    multicontext_path = MULTICONTEXT_QUAL / "multicontext_matrix.json"
    stateful_decision_path = STATEFUL_DECISION_QUAL / "decision_audit.json"
    stateful_claim_path = STATEFUL_DECISION_QUAL / "claim_ledger.json"
    third_holdout_path = THIRD_HOLDOUT_RUN / "stateful_transfer_report.json"
    sensitivity_manifest_path = SENSITIVITY_RUN / "manifest.json"
    fallback_policy_path = POLICY_QUAL / "fallback_policy.json"
    attribution_path = ATTRIBUTION_RUN / "error_attribution_report.json"
    governor_path = GOVERNOR_QUAL / "profile_governor_report.json"
    governor_cost_path = GOVERNOR_QUAL / "route_cost_trace.jsonl"
    stress_validation_path = STRESS_RUN / "stress_validation_report.json"
    boundary_path = BOUNDARY_RUN / "boundary_intervention_report.json"
    activation_coverage_path = ACTIVATION_COVERAGE_RUN / "activation_coverage_report.json"
    coverage_aware_governor_path = COVERAGE_AWARE_GOVERNOR_QUAL / "coverage_aware_profile_governor.json"
    calibration_v3_path = CALIBRATION_V3_RUN / "stateful_transfer_report.json"
    second_order_path = SECOND_ORDER_RUN / "stateful_transfer_report.json"
    input_energy_residual_path = INPUT_ENERGY_RESIDUAL_RUN / "context_transfer_report.json"
    module_error_decomposition_path = MODULE_ERROR_DECOMPOSITION_RUN / "module_error_decomposition_report.json"
    targeted_cproj_adc_path = TARGETED_CPROJ_ADC_RUN / "targeted_cproj_adc_report.json"
    targeted_cproj_transfer_path = TARGETED_CPROJ_TRANSFER_RUN / "targeted_cproj_adc_report.json"
    cproj_settling_path = CPROJ_SETTLING_RUN / "targeted_cproj_adc_report.json"
    cproj_state_machine_path = CPROJ_STATE_MACHINE_RUN / "targeted_cproj_adc_report.json"
    circuit_transfer_table_path = CIRCUIT_TRANSFER_TABLE_RUN / "circuit_transfer_table.json"
    transfer_table_policy_path = TRANSFER_TABLE_POLICY_RUN / "transfer_table_fallback_policy.json"
    transfer_table_runtime_path = TRANSFER_TABLE_RUNTIME_RUN / "transfer_table_runtime_trace.json"
    transformer_transfer_runtime_path = TRANSFORMER_TRANSFER_RUNTIME_RUN / "transformer_transfer_table_runtime_trace.json"
    transformer_fallback_audit_path = TRANSFORMER_FALLBACK_AUDIT_RUN / "transformer_fallback_output_audit.json"
    multi_decision = json.loads(multi_decision_path.read_text(encoding="utf-8")) if multi_decision_path.is_file() else {}

    gates = {
        "model": {"status": "measured_fixture_contract", "pass": json.loads(model_path.read_text(encoding="utf-8")).get("claim_status") == "measured", "evidence": bind(model_path)},
        "gpu": {"status": gpu_status, "pass": gpu_ready, "evidence": bind(receipt_path), "artifact_checks": artifact_checks},
        "digital_fallback": {"status": "evidence_present", "pass": hybrid_path.is_file(), "evidence": bind(hybrid_path)},
        "circuit": {"status": profile.get("status"), "pass": bool(profile.get("analog_authorized")) and physical.get("status", "").endswith("passed_boundary"), "evidence": {"profile": bind(profile_path), "latest_sweep": bind(physical_sweep), "latest_campaign": bind(physical_campaign), "one_bit_cell": bind(one_bit_cell), "isolated_cell": bind(isolated_cell), "isolated_long_acquisition": bind(isolated_long), "isolated_reservoir": bind(isolated_reservoir)}},
        "workload": {
            "status": "local_profile_to_workload_ready_external_gates_open",
            "pass": False,
            "evidence": {
                "handoff": bind(PRODUCT_ROOT / "END_TO_END_QUALIFICATION_HANDOFF.md"),
                "local_profile_to_workload_report": bind(local_report_path),
                "local_profile_to_workload_decision": bind(local_decision_path),
                "local_profile_to_workload_claim_ledger": bind(local_claim_ledger_path),
                "local_multimodule_report": bind(multi_report_path),
                "local_multimodule_decision": bind(multi_decision_path),
                "local_multimodule_claim_ledger": bind(multi_claim_ledger_path),
                "local_multimodule_runtime_trace": bind(multi_runtime_path),
                "local_multimodule_cost_trace": bind(multi_cost_path),
                "local_multimodule_sensitivity_report": bind(sensitivity_report_path),
                "local_multimodule_sensitivity_manifest": bind(sensitivity_manifest_path),
                "local_multimodule_fallback_policy": bind(fallback_policy_path),
                "local_multimodule_error_attribution": bind(attribution_path),
                "local_multimodule_profile_governor": bind(governor_path),
                "local_multimodule_profile_governor_cost": bind(governor_cost_path),
                "local_multimodule_governor_stress_validation": bind(stress_validation_path),
                "local_multimodule_expanded_calibration_fixture": bind(CALIBRATION_FIXTURE),
                "local_multimodule_error_budget": bind(error_budget_path),
                "local_multimodule_profile_design_sweep": bind(profile_sweep_path),
                "local_multimodule_profile_design_stress": bind(profile_stress_path),
                "local_multimodule_range_stress": bind(range_stress_path),
                "local_multimodule_transfer_model_sweep": bind(transfer_sweep_path),
                "local_multimodule_context_transfer": bind(context_transfer_path),
                "local_stateful_profile_governor": bind(stateful_governor_path),
                "local_stateful_profile_cost_trace": bind(stateful_cost_path),
                "local_multicontext_matrix": bind(multicontext_path),
                "local_stateful_multimodule_decision": bind(stateful_decision_path),
                "local_stateful_multimodule_claim_ledger": bind(stateful_claim_path),
                "local_stateful_third_holdout": bind(third_holdout_path),
                "local_multimodule_boundary_interventions": bind(boundary_path),
                "local_multicontext_activation_coverage": bind(activation_coverage_path),
                "local_coverage_aware_profile_governor": bind(coverage_aware_governor_path),
                "local_coverage_guided_calibration_fixture": bind(CALIBRATION_V3_FIXTURE),
                "local_coverage_guided_stateful_replay": bind(calibration_v3_path),
                "local_second_order_stateful_replay": bind(second_order_path),
                "local_input_energy_residual_replay": bind(input_energy_residual_path),
                "local_module_error_decomposition": bind(module_error_decomposition_path),
                "local_targeted_cproj_adc_mitigation": bind(targeted_cproj_adc_path),
                "local_targeted_cproj_transfer_correction": bind(targeted_cproj_transfer_path),
                "local_cproj_settling_sweep": bind(cproj_settling_path),
                "local_cproj_state_machine": bind(cproj_state_machine_path),
                "local_circuit_transfer_table": bind(circuit_transfer_table_path),
                "local_transfer_table_fallback_policy": bind(transfer_table_policy_path),
                "local_transfer_table_runtime_trace": bind(transfer_table_runtime_path),
                "local_transformer_transfer_table_runtime_trace": bind(transformer_transfer_runtime_path),
                "local_transformer_fallback_output_audit": bind(transformer_fallback_audit_path),
                "local_transformer_per_vector_fallback_fingerprint": bind(TRANSFORMER_FINGERPRINT_RUN / "per_vector_fallback_fingerprint.json"),
            },
            "local_decision": local_decision.get("analog_advantage_decision", "missing"),
            "local_analog_candidate_authorized": local_decision.get("analog_candidate_authorized", False),
            "local_multimodule_decision": multi_decision.get("decision", "missing"),
            "local_multimodule_analog_candidate_authorized": multi_decision.get("analog_candidate_authorized", False),
            "claim_boundary": "Local profile replay and accounting are complete as bounded evidence; matched hardware/GPU workload qualification remains open.",
        },
    }
    all_pass = all(gate["pass"] for gate in gates.values())
    report = {
        "schema_version": "end_to_end_model_to_chip_qualification_manifest.v1",
        "manifest_id": "model-to-chip-qualification-2026-09-11",
        "status": "ready_for_bounded_ship_no_ship_review" if all_pass else "blocked_pending_declared_gates",
        "analog_authorized": all_pass,
        "gates": gates,
        "decision": "ship_candidate" if all_pass else "digital_reference_and_fallback_only",
        "claim_boundary": "This manifest joins evidence and gate state; it does not convert fixture measurements into pretrained-model quality, silicon behavior, or production readiness.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"gpu_ready,{gpu_ready}")
    print(f"analog_authorized,{report['analog_authorized']}")
    print(f"manifest,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
