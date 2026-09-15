#!/usr/bin/env python3
"""Validate the cross-repository model-to-chip handoff and gate invariants."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
HANDOFF = ROOT / "END_TO_END_QUALIFICATION_HANDOFF.md"
MANIFEST = ROOT / "evidence" / "end-to-end-qualification-manifest.json"


def main() -> int:
    failures: list[str] = []
    if not HANDOFF.is_file():
        failures.append(f"missing handoff: {HANDOFF}")
    else:
        text = HANDOFF.read_text(encoding="utf-8")
        for required in ("## Authoritative goal", "## Repository handoff", "## Hard gates", "## Definition of done", "analog_authorized"):
            if required not in text:
                failures.append(f"handoff missing required section/text: {required}")
    if not MANIFEST.is_file():
        failures.append(f"missing manifest: {MANIFEST}")
        report = {}
    else:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if report.get("schema_version") != "end_to_end_model_to_chip_qualification_manifest.v1":
        failures.append("unexpected manifest schema")
    gates = report.get("gates", {})
    expected = {"model", "gpu", "digital_fallback", "circuit", "workload"}
    if set(gates) != expected:
        failures.append(f"gate set mismatch: {sorted(gates)}")
    for name, gate in gates.items():
        evidence = gate.get("evidence", {})
        stack = [evidence]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                if "path" in item and item.get("present") != "true":
                    failures.append(f"passing gate {name} references absent evidence: {item['path']}")
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
    workload_evidence = gates.get("workload", {}).get("evidence", {})
    local_report_entry = workload_evidence.get("local_profile_to_workload_report", {})
    local_decision_entry = workload_evidence.get("local_profile_to_workload_decision", {})
    local_claim_entry = workload_evidence.get("local_profile_to_workload_claim_ledger", {})
    for label, entry in (("local workload report", local_report_entry),
                         ("local workload decision", local_decision_entry),
                         ("local workload claim ledger", local_claim_entry)):
        if entry.get("present") == "true":
            path = WORKSPACE / entry["path"]
            if not path.is_file():
                failures.append(f"{label} is absent: {path}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != entry.get("sha256"):
                failures.append(f"{label} hash mismatch: {path}")
    for label in ("local_multimodule_report", "local_multimodule_decision",
                  "local_multimodule_claim_ledger", "local_multimodule_runtime_trace",
                  "local_multimodule_cost_trace", "local_multimodule_sensitivity_report",
                  "local_multimodule_sensitivity_manifest", "local_multimodule_fallback_policy",
                  "local_multimodule_error_attribution", "local_multimodule_profile_governor",
                  "local_multimodule_profile_governor_cost", "local_multimodule_governor_stress_validation",
                  "local_multimodule_expanded_calibration_fixture",
                  "local_multimodule_error_budget", "local_multimodule_profile_design_sweep",
                  "local_multimodule_profile_design_stress",
                  "local_multimodule_range_stress",
                  "local_multimodule_transfer_model_sweep",
                  "local_multimodule_context_transfer",
                  "local_stateful_profile_governor", "local_stateful_profile_cost_trace",
                  "local_multicontext_matrix",
                  "local_stateful_multimodule_decision", "local_stateful_multimodule_claim_ledger",
                  "local_stateful_third_holdout",
                  "local_multimodule_boundary_interventions",
                  "local_multicontext_activation_coverage",
                  "local_coverage_aware_profile_governor",
                  "local_coverage_guided_calibration_fixture",
                  "local_coverage_guided_stateful_replay",
                  "local_second_order_stateful_replay",
                  "local_input_energy_residual_replay",
                  "local_module_error_decomposition",
                  "local_targeted_cproj_adc_mitigation",
                  "local_targeted_cproj_transfer_correction",
                  "local_cproj_settling_sweep",
                  "local_cproj_state_machine",
                  "local_circuit_transfer_table",
                  "local_transfer_table_fallback_policy",
                  "local_transfer_table_runtime_trace",
                  "local_transformer_transfer_table_runtime_trace",
                  "local_transformer_fallback_output_audit",
                  "local_transformer_per_vector_fallback_fingerprint"):
        entry = workload_evidence.get(label, {})
        if entry.get("present") == "true":
            path = WORKSPACE / entry["path"]
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != entry.get("sha256"):
                failures.append(f"{label} hash mismatch or absence: {path}")
    multi_decision_entry = workload_evidence.get("local_multimodule_decision", {})
    if multi_decision_entry.get("present") == "true":
        multi_decision = json.loads((WORKSPACE / multi_decision_entry["path"]).read_text(encoding="utf-8"))
        if (multi_decision.get("decision") != "multi_module_hybrid_benefit_unproven"
                or multi_decision.get("analog_candidate_authorized") is not False):
                failures.append("multi-module workload decision bypasses the fail-closed authorization state")
    sensitivity_entry = workload_evidence.get("local_multimodule_sensitivity_report", {})
    if sensitivity_entry.get("present") == "true":
        sensitivity = json.loads((WORKSPACE / sensitivity_entry["path"]).read_text(encoding="utf-8"))
        if sensitivity.get("summary", {}).get("passing_screen_scenarios") != 2:
            failures.append("sensitivity campaign summary is not the retained bounded result")
    policy_entry = workload_evidence.get("local_multimodule_fallback_policy", {})
    if policy_entry.get("present") == "true":
        policy = json.loads((WORKSPACE / policy_entry["path"]).read_text(encoding="utf-8"))
        enforced = policy.get("enforced_policy", {})
        if (policy.get("decision") != "reject_partial_analog_policy_and_use_full_digital_fallback"
                or enforced.get("route") != "digital_fallback"
                or enforced.get("analog_authorized") is not False):
            failures.append("multi-module fallback policy is not fail-closed")
    attribution_entry = workload_evidence.get("local_multimodule_error_attribution", {})
    if attribution_entry.get("present") == "true":
        attribution = json.loads((WORKSPACE / attribution_entry["path"]).read_text(encoding="utf-8"))
        if attribution.get("interaction_summary", {}).get("full_to_isolated_sum_ratio", 0) >= 1:
            failures.append("error attribution does not preserve the bounded interaction finding")
    governor_entry = workload_evidence.get("local_multimodule_profile_governor", {})
    if governor_entry.get("present") == "true":
        governor = json.loads((WORKSPACE / governor_entry["path"]).read_text(encoding="utf-8"))
        if (governor.get("decision") != "full_digital_fallback"
                or governor.get("enforced_policy", {}).get("analog_authorized") is not False):
            failures.append("profile governor is not fail-closed")
    stress_entry = workload_evidence.get("local_multimodule_governor_stress_validation", {})
    if stress_entry.get("present") == "true":
        stress = json.loads((WORKSPACE / stress_entry["path"]).read_text(encoding="utf-8"))
        if (stress.get("decision") != "numerical_recommendation_does_not_generalize_and_hardware_authorization_remains_closed"
                or any(row.get("screen_pass") for row in stress.get("results", {}).values())):
            failures.append("governor stress validation does not preserve negative generalization")
    error_budget_entry = workload_evidence.get("local_multimodule_error_budget", {})
    if error_budget_entry.get("present") == "true":
        error_budget = json.loads((WORKSPACE / error_budget_entry["path"]).read_text(encoding="utf-8"))
        if error_budget.get("configurations", {}).get("weight_quantization_only", {}).get("quality", {}).get("screen_pass") is not True:
            failures.append("error budget does not preserve the passing weight-only control")
    profile_stress_entry = workload_evidence.get("local_multimodule_profile_design_stress", {})
    if profile_stress_entry.get("present") == "true":
        profile_stress = json.loads((WORKSPACE / profile_stress_entry["path"]).read_text(encoding="utf-8"))
        if any(row.get("screen_pass") for row in profile_stress.get("results", {}).values()):
            failures.append("redesigned profile stress evidence contains an unexpected pass")
    range_stress_entry = workload_evidence.get("local_multimodule_range_stress", {})
    if range_stress_entry.get("present") == "true":
        range_stress = json.loads((WORKSPACE / range_stress_entry["path"]).read_text(encoding="utf-8"))
        if range_stress.get("results", {}).get("full_three_module", {}).get("screen_pass") is not False:
            failures.append("range-stress full route unexpectedly passed")
    transfer_entry = workload_evidence.get("local_multimodule_transfer_model_sweep", {})
    if transfer_entry.get("present") == "true":
        transfer = json.loads((WORKSPACE / transfer_entry["path"]).read_text(encoding="utf-8"))
        if len(transfer.get("passing_results", [])) != 2:
            failures.append("transfer-model sweep does not preserve the cross-split boundary")
    context_entry = workload_evidence.get("local_multimodule_context_transfer", {})
    if context_entry.get("present") == "true":
        context = json.loads((WORKSPACE / context_entry["path"]).read_text(encoding="utf-8"))
        if context.get("passing_results") != ["global_affine_stress", "magnitude_context_affine_original"]:
            failures.append("context-transfer sweep does not preserve the cross-split boundary")
    stateful_entry = workload_evidence.get("local_stateful_profile_governor", {})
    if stateful_entry.get("present") == "true":
        stateful = json.loads((WORKSPACE / stateful_entry["path"]).read_text(encoding="utf-8"))
        if (stateful.get("decision") != "stateful_profile_numerically_qualified_but_digital_fallback_enforced"
                or stateful.get("enforced_policy", {}).get("analog_authorized") is not False):
            failures.append("stateful profile governor is not fail-closed")
    third_holdout_entry = workload_evidence.get("local_stateful_third_holdout", {})
    if third_holdout_entry.get("present") == "true":
        third_holdout = json.loads((WORKSPACE / third_holdout_entry["path"]).read_text(encoding="utf-8"))
        if third_holdout.get("results", {}).get("stateful_previous_token_original", {}).get("quality", {}).get("screen_pass") is not False:
            failures.append("stateful third holdout unexpectedly passed")
    multicontext_entry = workload_evidence.get("local_multicontext_matrix", {})
    if multicontext_entry.get("present") == "true":
        multicontext = json.loads((WORKSPACE / multicontext_entry["path"]).read_text(encoding="utf-8"))
        if multicontext.get("all_contexts_pass") is not False:
            failures.append("multi-context matrix unexpectedly passed")
    coverage_entry = workload_evidence.get("local_multicontext_activation_coverage", {})
    if coverage_entry.get("present") == "true":
        coverage = json.loads((WORKSPACE / coverage_entry["path"]).read_text(encoding="utf-8"))
        if coverage.get("schema_version") != "gpt2-multicontext-activation-coverage-v0.1":
            failures.append("activation coverage schema is unexpected")
        if set(coverage.get("contexts", {})) != {"calibration", "original", "stress", "third_holdout"}:
            failures.append("activation coverage contexts are incomplete")
        if "Local CPU" not in coverage.get("claim_boundary", "") or "analog authorization" not in coverage.get("claim_boundary", ""):
            failures.append("activation coverage claim boundary is too broad")
    coverage_governor_entry = workload_evidence.get("local_coverage_aware_profile_governor", {})
    if coverage_governor_entry.get("present") == "true":
        coverage_governor = json.loads((WORKSPACE / coverage_governor_entry["path"]).read_text(encoding="utf-8"))
        policy = coverage_governor.get("enforced_policy", {})
        if (coverage_governor.get("decision") != "coverage_out_of_envelope_full_digital_fallback"
                or not coverage_governor.get("coverage_gate", {}).get("out_of_envelope")
                or policy.get("route") != "digital_fallback"
                or coverage_governor.get("analog_authorized") is not False):
            failures.append("coverage-aware profile governor is not fail-closed")
    guided_replay_entry = workload_evidence.get("local_coverage_guided_stateful_replay", {})
    if guided_replay_entry.get("present") == "true":
        guided_replay = json.loads((WORKSPACE / guided_replay_entry["path"]).read_text(encoding="utf-8"))
        results = guided_replay.get("results", {})
        if (results.get("stateful_previous_token_original", {}).get("quality", {}).get("screen_pass") is not True
                or results.get("stateful_previous_token_stress", {}).get("quality", {}).get("screen_pass") is not True
                or results.get("stateful_previous_token_third_holdout", {}).get("quality", {}).get("screen_pass") is not False):
            failures.append("coverage-guided replay did not preserve the two-pass/third-holdout-fail boundary")
    second_order_entry = workload_evidence.get("local_second_order_stateful_replay", {})
    if second_order_entry.get("present") == "true":
        second_order = json.loads((WORKSPACE / second_order_entry["path"]).read_text(encoding="utf-8"))
        results = second_order.get("results", {})
        if (results.get("stateful_previous_two_tokens_original", {}).get("quality", {}).get("screen_pass") is not True
                or results.get("stateful_previous_two_tokens_stress", {}).get("quality", {}).get("screen_pass") is not False
                or results.get("stateful_previous_two_tokens_third_holdout", {}).get("quality", {}).get("screen_pass") is not False
                or second_order.get("analog_authorized") is not False):
            failures.append("second-order stateful replay did not preserve its negative generalization boundary")
    input_energy_entry = workload_evidence.get("local_input_energy_residual_replay", {})
    if input_energy_entry.get("present") == "true":
        input_energy = json.loads((WORKSPACE / input_energy_entry["path"]).read_text(encoding="utf-8"))
        results = input_energy.get("results", {})
        if any(results.get(f"input_energy_residual_affine_{dataset}", {}).get("quality", {}).get("screen_pass") is not False
               for dataset in ("original", "stress", "third_holdout")):
            failures.append("input-energy residual replay did not preserve its negative boundary")
        if input_energy.get("analog_authorized") is not False:
            failures.append("input-energy residual replay authorized analog execution")
    decomposition_entry = workload_evidence.get("local_module_error_decomposition", {})
    if decomposition_entry.get("present") == "true":
        decomposition = json.loads((WORKSPACE / decomposition_entry["path"]).read_text(encoding="utf-8"))
        if (decomposition.get("finding", {}).get("dominant_module") != "transformer.h.0.mlp.c_proj"
                or decomposition.get("decision") != "c_proj_boundary_and_adc_resolution_are_the_next_local_targets"
                or decomposition.get("analog_authorized") is not False):
            failures.append("module error decomposition did not preserve the c_proj/ADC boundary")
    targeted_adc_entry = workload_evidence.get("local_targeted_cproj_adc_mitigation", {})
    if targeted_adc_entry.get("present") == "true":
        targeted_adc = json.loads((WORKSPACE / targeted_adc_entry["path"]).read_text(encoding="utf-8"))
        results = targeted_adc.get("results", {})
        expected = {"original": True, "stress": False, "third_holdout": False}
        if any(results.get(f"c_proj_adc16_only_{dataset}", {}).get("quality", {}).get("screen_pass") is not expected_pass
               for dataset, expected_pass in expected.items()):
            failures.append("targeted c_proj ADC mitigation did not preserve its two-boundary result")
        if targeted_adc.get("decision") != "c_proj_adc16_does_not_generalize" or targeted_adc.get("analog_authorized") is not False:
            failures.append("targeted c_proj ADC mitigation decision is unsafe")
    targeted_transfer_entry = workload_evidence.get("local_targeted_cproj_transfer_correction", {})
    if targeted_transfer_entry.get("present") == "true":
        targeted_transfer = json.loads((WORKSPACE / targeted_transfer_entry["path"]).read_text(encoding="utf-8"))
        if targeted_transfer.get("quadratic_decision") != "c_proj_quadratic_does_not_generalize" or targeted_transfer.get("analog_authorized") is not False:
            failures.append("targeted c_proj transfer correction decision is unsafe")
    settling_entry = workload_evidence.get("local_cproj_settling_sweep", {})
    if settling_entry.get("present") == "true":
        settling = json.loads((WORKSPACE / settling_entry["path"]).read_text(encoding="utf-8"))
        if (set(settling.get("settling_decisions", {})) != {"c_proj_settling_001", "c_proj_settling_01", "c_proj_settling_05"}
                or any(value != "does_not_generalize" for value in settling["settling_decisions"].values())
                or settling.get("analog_authorized") is not False):
            failures.append("c_proj settling sweep did not preserve its negative generalization boundary")
    state_machine_entry = workload_evidence.get("local_cproj_state_machine", {})
    if state_machine_entry.get("present") == "true":
        state_machine = json.loads((WORKSPACE / state_machine_entry["path"]).read_text(encoding="utf-8"))
        results = state_machine.get("results", {})
        if any(results.get(f"c_proj_state_machine_095_01_{dataset}", {}).get("quality", {}).get("screen_pass") is not False
               for dataset in ("original", "stress", "third_holdout")):
            failures.append("c_proj reduced-charge state-machine result changed")
        if any(results.get(f"c_proj_state_machine_1_01_{dataset}", {}).get("quality", {}).get("screen_pass") is not (dataset != "third_holdout")
               for dataset in ("original", "stress", "third_holdout")):
            failures.append("c_proj full-charge state-machine result changed")
    circuit_table_entry = workload_evidence.get("local_circuit_transfer_table", {})
    if circuit_table_entry.get("present") == "true":
        circuit_table = json.loads((WORKSPACE / circuit_table_entry["path"]).read_text(encoding="utf-8"))
        binding = circuit_table.get("adapter_binding", {})
        if (circuit_table.get("requested_code_count") != 16
                or circuit_table.get("measured_code_count") != 6
                or circuit_table.get("complete_code_map") is not False
                or binding.get("status") != "refused_incomplete_code_map"
                or binding.get("bound_to_workload") is not False
                or circuit_table.get("analog_authorized") is not False):
            failures.append("partial circuit transfer table was not kept unbound and fail-closed")
    transfer_policy_entry = workload_evidence.get("local_transfer_table_fallback_policy", {})
    if transfer_policy_entry.get("present") == "true":
        transfer_policy = json.loads((WORKSPACE / transfer_policy_entry["path"]).read_text(encoding="utf-8"))
        routes = transfer_policy.get("routes", {})
        if (transfer_policy.get("unsupported_codes") != [0, 2, 3, 4, 5, 6, 7, 9, 11, 12]
                or len(routes) != 16
                or any(route.get("route") != "digital_fallback" for route in routes.values())
                or transfer_policy.get("overall_route") != "digital_fallback"
                or transfer_policy.get("analog_authorized") is not False):
            failures.append("transfer-table missing-code fallback policy is incomplete or unsafe")
    transfer_runtime_entry = workload_evidence.get("local_transfer_table_runtime_trace", {})
    if transfer_runtime_entry.get("present") == "true":
        transfer_runtime = json.loads((WORKSPACE / transfer_runtime_entry["path"]).read_text(encoding="utf-8"))
        events = transfer_runtime.get("events", [])
        if (len(events) != 16
                or [event.get("requested_converter_code") for event in events] != list(range(16))
                or transfer_runtime.get("unsupported_code_events") != [0, 2, 3, 4, 5, 6, 7, 9, 11, 12]
                or transfer_runtime.get("all_routes_fallback") is not True
                or transfer_runtime.get("analog_instruction_count") != 0):
            failures.append("transfer-table runtime trace does not enforce all-code fallback")
    transformer_transfer_entry = workload_evidence.get("local_transformer_transfer_table_runtime_trace", {})
    if transformer_transfer_entry.get("present") == "true":
        transformer_transfer = json.loads((WORKSPACE / transformer_transfer_entry["path"]).read_text(encoding="utf-8"))
        events = transformer_transfer.get("events", [])
        if (len(events) != 162
                or transformer_transfer.get("workload_vectors") != 162
                or transformer_transfer.get("all_routes_fallback") is not True
                or transformer_transfer.get("all_unsupported_codes_explicit") is not True
                or transformer_transfer.get("analog_instruction_count") != 0):
            failures.append("transformer all-code fallback binding is incomplete or unsafe")
    fallback_audit_entry = workload_evidence.get("local_transformer_fallback_output_audit", {})
    if fallback_audit_entry.get("present") == "true":
        fallback_audit = json.loads((WORKSPACE / fallback_audit_entry["path"]).read_text(encoding="utf-8"))
        if (fallback_audit.get("scheduled_vectors") != 162
                or fallback_audit.get("scheduled_routes_all_fallback") is not True
                or fallback_audit.get("exact_fallback_context_count") != 4
                or fallback_audit.get("exact_logits_and_generation_checked") is not True
                or fallback_audit.get("per_vector_tensor_parity_retained") is not False
                or fallback_audit.get("analog_authorized") is not False):
            failures.append("fallback output audit is incomplete or overclaims exact parity")
    fingerprint_entry = workload_evidence.get("local_transformer_per_vector_fallback_fingerprint", {})
    if fingerprint_entry.get("present") == "true":
        fingerprint = json.loads((WORKSPACE / fingerprint_entry["path"]).read_text(encoding="utf-8"))
        if (fingerprint.get("workload_vectors") != 162
                or fingerprint.get("all_modules_numerically_equal") is not True
                or fingerprint.get("total_mismatch_count") != 84
                or fingerprint.get("analog_authorized") is not False):
            failures.append("per-vector fallback fingerprint is incomplete or overclaims parity")
    stateful_decision_entry = workload_evidence.get("local_stateful_multimodule_decision", {})
    if stateful_decision_entry.get("present") == "true":
        stateful_decision = json.loads((WORKSPACE / stateful_decision_entry["path"]).read_text(encoding="utf-8"))
        if (stateful_decision.get("decision") != "stateful_profile_not_generalized"
                or stateful_decision.get("analog_candidate_authorized") is not False):
            failures.append("stateful multi-module decision is not fail-closed")
    boundary_entry = workload_evidence.get("local_multimodule_boundary_interventions", {})
    if boundary_entry.get("present") == "true":
        boundary = json.loads((WORKSPACE / boundary_entry["path"]).read_text(encoding="utf-8"))
        if boundary.get("amplitudes") != [0.25, 0.5, 1.0, 2.0]:
            failures.append("boundary intervention matrix is incomplete")
    if (local_report_entry.get("present") == "true" and local_decision_entry.get("present") == "true"
            and local_claim_entry.get("present") == "true"):
        local_report_path = WORKSPACE / local_report_entry["path"]
        local_decision_path = WORKSPACE / local_decision_entry["path"]
        local_claim_path = WORKSPACE / local_claim_entry["path"]
        if local_report_path.is_file() and local_decision_path.is_file() and local_claim_path.is_file():
            local_report = json.loads(local_report_path.read_text(encoding="utf-8"))
            local_decision = json.loads(local_decision_path.read_text(encoding="utf-8"))
            local_claims = json.loads(local_claim_path.read_text(encoding="utf-8"))
            if local_report.get("decision") != "digital_reference_and_deterministic_fallback_only":
                failures.append("local workload report has an unsafe or unexpected decision")
            if (local_decision.get("analog_candidate_authorized") is not False
                    or local_decision.get("runtime_decision") != "digital_reference_and_deterministic_fallback_only"):
                failures.append("local workload decision bypasses the fail-closed authorization state")
            if (local_claims.get("result_type") != "claim_scoped_local_model_to_workload_evidence"
                    or any(row.get("status") == "authorized" for row in local_claims.get("claims", []))):
                failures.append("local workload claim ledger contains an unsafe authorization status")
    if report.get("analog_authorized") is not all(gate.get("pass") is True for gate in gates.values()):
        failures.append("analog_authorized does not equal all declared gates passing")
    if report.get("analog_authorized") is not True and report.get("decision") != "digital_reference_and_fallback_only":
        failures.append("blocked manifest has an unsafe decision")
    if failures:
        print("END-TO-END HANDOFF INVALID")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print(f"END-TO-END HANDOFF OK: {len(gates)} gates; analog_authorized={report['analog_authorized']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
