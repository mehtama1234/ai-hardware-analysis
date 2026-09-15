#!/usr/bin/env python3
"""Fail-closed checker for the local profile-to-workload package."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]


def resolve_source(path: Path) -> Path:
    if path.is_absolute() or path.exists():
        return path
    workspace_path = WORKSPACE / path
    return workspace_path if workspace_path.exists() else path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    report_path = args.package / "qualification_report.json"
    manifest_path = args.package / "manifest.json"
    execution_path = args.package / "execution_trace.jsonl"
    injection_path = args.package / "failure_injection_replay.json"
    tensor_path = args.package / "tensor_outputs.npz"
    governor_path = args.package / "threshold_governor_trace.jsonl"
    runtime_trace_path = args.package / "workload_runtime_trace.json"
    cost_trace_path = args.package / "workload_cost_trace.jsonl"
    calibration_path = args.package / "calibration_correction.npz"
    calibrated_tensor_path = args.package / "calibrated_tensor_outputs.npz"
    decision_path = args.package / "decision_audit.json"
    claim_ledger_path = args.package / "claim_ledger.json"
    final_doc_path = args.package / "final_decision.md"
    failures = []
    for path in (report_path, manifest_path, execution_path, injection_path, tensor_path, governor_path,
                 runtime_trace_path,
                 cost_trace_path,
                 calibration_path, calibrated_tensor_path, decision_path, claim_ledger_path, final_doc_path):
        if not path.exists():
            failures.append(f"missing {path.name}")
    if failures:
        raise SystemExit("LOCAL PACKAGE FAILED: " + "; ".join(failures))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name, source in report.get("sources", {}).items():
        source_path = resolve_source(Path(source.get("path", "")))
        if not source_path.is_file():
            failures.append(f"source receipt missing: {name}: {source_path}")
        elif sha256(source_path) != source.get("sha256"):
            failures.append(f"source receipt hash mismatch: {name}: {source_path}")
    if manifest.get("report", {}).get("sha256") != sha256(report_path):
        failures.append("manifest report hash mismatch")
    if manifest.get("execution_trace", {}).get("sha256") != sha256(execution_path):
        failures.append("manifest execution trace hash mismatch")
    if manifest.get("failure_injection_replay", {}).get("sha256") != sha256(injection_path):
        failures.append("manifest failure-injection replay hash mismatch")
    if manifest.get("tensor_outputs", {}).get("sha256") != sha256(tensor_path):
        failures.append("manifest tensor output hash mismatch")
    if manifest.get("threshold_governor", {}).get("sha256") != sha256(governor_path):
        failures.append("manifest threshold governor hash mismatch")
    if manifest.get("workload_runtime_trace", {}).get("sha256") != sha256(runtime_trace_path):
        failures.append("manifest workload runtime trace hash mismatch")
    if manifest.get("workload_cost_trace", {}).get("sha256") != sha256(cost_trace_path):
        failures.append("manifest workload cost trace hash mismatch")
    if manifest.get("calibration_correction", {}).get("sha256") != sha256(calibration_path):
        failures.append("manifest calibration correction hash mismatch")
    if manifest.get("calibrated_tensor_outputs", {}).get("sha256") != sha256(calibrated_tensor_path):
        failures.append("manifest calibrated tensor output hash mismatch")
    if manifest.get("decision_audit", {}).get("sha256") != sha256(decision_path):
        failures.append("manifest decision audit hash mismatch")
    if manifest.get("claim_ledger", {}).get("sha256") != sha256(claim_ledger_path):
        failures.append("manifest claim ledger hash mismatch")
    if report.get("decision") != "digital_reference_and_deterministic_fallback_only":
        failures.append("unexpected decision")
    if report.get("profile_gate", {}).get("analog_authorized") is not False:
        failures.append("analog authorization must remain false")
    selected = report.get("error_sensitivity", {}).get("selected_profile_quality_pass")
    if selected is not True:
        failures.append("selected numerical quality screen did not pass")
    envelope = report.get("error_sensitivity", {}).get("per_vector_relative_l2_envelope", {})
    if not envelope.get("passing_vector_counts") or any(
        not isinstance(value, int) or value < 0
        for value in envelope["passing_vector_counts"].values()
    ):
        failures.append("per-vector quality envelope is missing or invalid")
    calibrated_envelope = report.get("error_sensitivity", {}).get("calibrated_per_vector_relative_l2_envelope", {})
    calibrated_counts = calibrated_envelope.get("passing_vector_counts", {})
    if calibrated_envelope.get("input") != "calibrated_tensor_replay" or set(calibrated_counts) != {
        "0.001", "0.002", "0.005", "0.01", "0.02", "0.03"
    } or any(not isinstance(value, int) or value < 0 or value > report.get("workload", {}).get("vectors", 0)
             for value in calibrated_counts.values()):
        failures.append("calibrated per-vector quality envelope is missing or invalid")
    fallback_contexts = report.get("output_replay", {}).get("digital_fallback_contexts", [])
    if not fallback_contexts or not all(row.get("output_equivalent") is True for row in fallback_contexts):
        failures.append("digital fallback output replay is not exact for every recorded context")
    if report.get("output_replay", {}).get("fallback_all_contexts_exact") is not True:
        failures.append("fallback aggregate exactness guard failed")
    tensor = report.get("tensor_replay", {})
    tensor_rows = tensor.get("records", [])
    if tensor.get("record_count") != len(tensor_rows) or len(tensor_rows) != report.get("workload", {}).get("vectors"):
        failures.append("tensor replay record count does not match workload vectors")
    if tensor_rows and [row.get("vector_id") for row in tensor_rows] != list(range(len(tensor_rows))):
        failures.append("tensor replay vector ordering is not contiguous")
    if tensor.get("ideal_variant") != "ideal_tiled_control" or tensor.get("hybrid_variant") != "dac10_weight8_adc12":
        failures.append("tensor replay variants are not the declared ideal and ADC12 pair")
    try:
        import numpy as np
        with np.load(tensor_path) as arrays:
            if arrays["ideal_tiled_control"].shape != arrays["dac10_weight8_adc12"].shape:
                failures.append("tensor output arrays have mismatched shapes")
            if arrays["ideal_tiled_control"].shape[0] != len(tensor_rows):
                failures.append("tensor output row count does not match tensor replay")
    except Exception as exc:
        failures.append(f"tensor output artifact unreadable: {exc}")
    governor_rows = [json.loads(row) for row in governor_path.read_text(encoding="utf-8").splitlines()]
    if len(governor_rows) != len(tensor_rows):
        failures.append("threshold governor row count does not match tensor replay")
    if any(row.get("enforced_route") != "digital_fallback" for row in governor_rows):
        failures.append("threshold governor emitted an unauthorized analog route")
    if any(row.get("eligible_for_analog_candidate") is not False for row in governor_rows):
        failures.append("threshold governor eligibility guard failed")
    if any(not row.get("rejection_reasons") for row in governor_rows):
        failures.append("threshold governor accepted a vector without a rejection reason")
    runtime_trace = json.loads(runtime_trace_path.read_text(encoding="utf-8"))
    agreement = runtime_trace.get("trace_agreement", {})
    if runtime_trace.get("workload_vectors") != len(tensor_rows) or runtime_trace.get("totals", {}).get("event_count") != len(tensor_rows):
        failures.append("workload runtime trace count is inconsistent")
    if agreement.get("execution_vector_ids_match") is not True or agreement.get("governor_vector_ids_match") is not True:
        failures.append("workload runtime trace does not agree with source traces")
    if agreement.get("all_routes_fallback") is not True or runtime_trace.get("totals", {}).get("analog_events") != 0:
        failures.append("workload runtime trace contains an analog route")
    cost_rows = [json.loads(row) for row in cost_trace_path.read_text(encoding="utf-8").splitlines()]
    if len(cost_rows) != len(tensor_rows) or [row.get("vector_id") for row in cost_rows] != list(range(len(cost_rows))):
        failures.append("workload cost trace count or ordering is inconsistent")
    if any(row.get("enforced_route") != "digital_fallback"
           or row.get("enforced_route_cost_pj", 0) <= 0
           or row.get("digital_reference_cycles", 0) <= 0
           or row.get("counterfactual_hybrid_cycles", 0) <= 0
           or row.get("analog_authorized") is not False
           for row in cost_rows):
        failures.append("workload cost trace contains invalid route or accounting rows")
    accounting_ledger = report.get("workload_accounting", {}).get("per_vector_ledger", {})
    if accounting_ledger.get("row_count") != len(cost_rows):
        failures.append("workload accounting ledger metadata is inconsistent")
    accounting = report.get("workload_accounting", {})
    if cost_rows:
        def close(actual, expected):
            return math.isclose(float(actual), float(expected), rel_tol=1e-9, abs_tol=1e-6)
        if not close(sum(row["digital_reference_cost_pj"] for row in cost_rows), accounting.get("digital_reference_cost_pj", -1)):
            failures.append("per-vector digital cost does not reconcile to aggregate")
        if not close(sum(row["counterfactual_hybrid_cost_pj"] for row in cost_rows), accounting.get("counterfactual_hybrid_cost_pj", -1)):
            failures.append("per-vector hybrid cost does not reconcile to aggregate")
        if not close(sum(row["enforced_route_cost_pj"] for row in cost_rows), accounting.get("digital_reference_cost_pj", -1)):
            failures.append("per-vector enforced route cost does not reconcile to fallback total")
        timing_model = accounting.get("timing_model", {})
        if not close(sum(row["digital_reference_cycles"] for row in cost_rows), timing_model.get("digital_reference_cycles", -1)):
            failures.append("per-vector digital timing does not reconcile to aggregate")
        if not close(sum(row["counterfactual_hybrid_cycles"] for row in cost_rows), timing_model.get("counterfactual_hybrid_cycles", -1)):
            failures.append("per-vector hybrid timing does not reconcile to aggregate")
    calibration = report.get("calibration_replay", {})
    if calibration.get("present") is not True or calibration.get("split_disjoint") is not True:
        failures.append("disjoint calibration receipt is missing or not disjoint")
    if (calibration.get("calibration_metrics") or {}).get("method") != "per-output-channel affine gain and offset correction":
        failures.append("calibration method is not the declared affine correction")
    calibrated = calibration.get("held_out_calibrated_quality") or {}
    if calibrated.get("teacher_forced_argmax_agreement") != 1.0 or calibrated.get("generation_exact_match_count") != 4:
        failures.append("calibrated held-out quality control failed")
    try:
        import numpy as np
        with np.load(calibration_path) as arrays:
            if arrays["output_scale"].shape != (3072,):
                failures.append("calibration scale shape is not [3072]")
            if arrays["output_correction"].shape != (3072,):
                failures.append("calibration correction shape is not [3072]")
    except Exception as exc:
        failures.append(f"calibration correction artifact unreadable: {exc}")
    generalization = report.get("calibration_generalization", {})
    receipt = generalization.get("receipt") or {}
    if generalization.get("present") is not True or receipt.get("decision") != "mixed_calibration_generalization":
        failures.append("cross-split calibration generalization receipt is missing or misclassified")
    calibrated_tensor = report.get("calibrated_tensor_replay", {})
    if calibrated_tensor.get("present") is not True or calibrated_tensor.get("record_count") != len(tensor_rows):
        failures.append("calibrated tensor replay is missing or incomplete")
    try:
        import numpy as np
        with np.load(calibrated_tensor_path) as arrays:
            if arrays["adc12_calibrated"].shape[0] != len(tensor_rows):
                failures.append("calibrated tensor row count does not match workload")
    except Exception as exc:
        failures.append(f"calibrated tensor artifact unreadable: {exc}")
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    if decision.get("analog_candidate_authorized") is not False or decision.get("runtime_decision") != "digital_reference_and_deterministic_fallback_only":
        failures.append("decision audit authorization or runtime decision guard failed")
    if decision.get("analog_advantage_decision") != "unresolved" or decision.get("gate_count") != 9:
        failures.append("decision audit is incomplete or overclaims analog advantage")
    claim_ledger = json.loads(claim_ledger_path.read_text(encoding="utf-8"))
    claims = {row.get("claim"): row.get("status") for row in claim_ledger.get("claims", [])}
    required_claims = {
        "frozen_workload_and_tensor_replay": "proven_local",
        "held_out_model_quality": "proven_local_bounded",
        "disjoint_software_calibration_generalization": "proven_local_bounded",
        "per_vector_one_percent_tensor_quality": "not_proven",
        "complete_converter_profile": "blocked",
        "measured_per_vector_timing": "not_measured",
        "matched_energy_or_cost_advantage": "modeled_only",
        "compiler_runtime_trace_agreement": "proven_local_bounded",
        "analog_execution_authorization": "not_authorized",
    }
    if claims != required_claims or claim_ledger.get("result_type") != "claim_scoped_local_model_to_workload_evidence":
        failures.append("claim ledger is incomplete or has unsafe claim status")
    sweep = report.get("threshold_sweep", {}).get("rows", [])
    if len(sweep) != 6 or any(row.get("actual_analog_eligible_vectors") != 0
                               or row.get("actual_route") != "digital_fallback" for row in sweep):
        failures.append("threshold sweep is incomplete or bypasses fail-closed routing")
    accounting = report.get("workload_accounting", {})
    sensitivity = accounting.get("sensitivity_matrix", [])
    if len(sensitivity) != 12 or any(
        row.get("actual_guarded_route") != "digital_fallback"
        or not isinstance(row.get("counterfactual_hybrid_lower_cost"), bool)
        or row.get("counterfactual_hybrid_cost_pj", -1) < 0
        for row in sensitivity
    ):
        failures.append("cost break-even sensitivity matrix is missing or invalid")
    break_even = accounting.get("break_even", {})
    if break_even.get("analog_mac_pj_at_equal_cost", 0) <= 0 or break_even.get("converter_value_pj_at_equal_cost", 0) <= 0:
        failures.append("cost break-even coefficients are missing or non-positive")
    amortization = accounting.get("calibration_amortization", [])
    if len(amortization) != 5 or any(
        row.get("inference_workloads_amortizing_calibration", 0) <= 0
        or row.get("counterfactual_hybrid_cost_with_amortized_calibration_pj", -1) < 0
        for row in amortization
    ):
        failures.append("calibration amortization sensitivity is missing or invalid")
    timing = accounting.get("timing_model", {})
    if timing.get("status") != "not_evaluated_no_budget_declared":
        failures.append("local timing model must remain explicitly unmeasured without a declared budget")
    if timing.get("digital_reference_cycles", -1) <= 0 or timing.get("counterfactual_hybrid_cycles", -1) <= 0:
        failures.append("counterfactual timing model is missing positive operation-count totals")
    if timing.get("analog_array_cycle_at_equal_cost", 0) <= 0:
        failures.append("timing break-even coefficient is missing or non-positive")
    profile_stress = report.get("profile_open_case_stress", {})
    open_cases = report.get("profile_gate", {}).get("open_cases", [])
    stress_cases = profile_stress.get("cases", [])
    if profile_stress.get("case_count") != len(open_cases) or len(stress_cases) != len(open_cases):
        failures.append("open profile-case stress coverage is incomplete")
    if any(row.get("enforced_route") != "digital_fallback" for row in stress_cases):
        failures.append("open profile-case stress bypassed digital fallback")
    injection = json.loads(injection_path.read_text(encoding="utf-8"))
    if injection.get("record_count") != len(injection.get("scenarios", [])):
        failures.append("failure-injection record count is inconsistent")
    if injection.get("record_count", 0) < 20 or injection.get("all_outputs_equivalent") is not True:
        failures.append("failure-injection replay is incomplete or not exact")
    if any(row.get("route") != "digital_fallback" for row in injection.get("scenarios", [])):
        failures.append("failure-injection replay contains an analog route")
    if report.get("workload", {}).get("vectors", 0) <= 0:
        failures.append("workload vector count must be positive")
    rows = execution_path.read_text(encoding="utf-8").splitlines()
    if len(rows) != report.get("workload", {}).get("vectors"):
        failures.append("execution trace row count does not match workload vectors")
    else:
        trace_rows = [json.loads(row) for row in rows]
        if not all(row.get("guarded_runtime_route") == "digital_fallback" for row in trace_rows):
            failures.append("execution trace contains an unauthorized analog route")
        if not all(row.get("analog_authorized") is False for row in trace_rows):
            failures.append("execution trace authorization guard failed")
    scenarios = report.get("fallback_injection", [])
    if len(scenarios) < 5 or not all(row.get("fallback_fraction") == 1.0 for row in scenarios):
        failures.append("fallback scenarios are incomplete or not fail-closed")
    runtime = report.get("compiler_runtime", {})
    if runtime.get("event_count", 0) <= 0 or not runtime.get("trace_has_fallback"):
        failures.append("compiler fallback trace is missing")
    output = {"status": "passed" if not failures else "failed",
              "checks": ["manifest_hash", "decision_guard", "authorization_guard",
                         "quality_screen", "output_replay", "tensor_replay", "threshold_governor",
                         "threshold_sweep", "calibration_replay", "workload_runtime_trace",
                         "decision_audit",
                         "failure_injection_replay",
                         "workload_count", "execution_trace",
                         "fallback_matrix",
                         "runtime_trace"],
              "failures": failures,
              "claim_boundary": report.get("claim_boundary")}
    print(json.dumps(output, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
