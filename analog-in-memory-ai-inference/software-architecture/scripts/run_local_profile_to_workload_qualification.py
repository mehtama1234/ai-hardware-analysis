#!/usr/bin/env python3
"""Build a local, claim-safe profile-to-workload qualification package.

This joins already recorded numerical evidence.  It does not manufacture
silicon, GPU, or measured-energy evidence.  The hybrid cost is explicitly a
counterfactual model and the guarded runtime is expected to fall back while
the physical converter gate is open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from threshold_governor import decide_vector


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
DEFAULT_RUN = ROOT / "experiments/gpt2-hybrid-v1/runs/20260910-profile-driven-colab"
QUAL = ROOT / "experiments/gpt2-hybrid-v1/qualification"
DEFAULT_EDA_TRACE = (ROOT.parent.parent / "analog-digital-chip-design-eda" /
                     "evidence/aimc-hybrid-compiler-runtime/guarded_hybrid_workload_runtime_trace.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_workspace_path(path: Path) -> Path:
    """Resolve a path emitted by a receipt, including workspace-relative paths."""
    if path.is_absolute() or path.exists():
        return path
    workspace_path = WORKSPACE / path
    return workspace_path if workspace_path.exists() else path


def quality_row(variant: dict[str, Any]) -> dict[str, Any]:
    quality = variant.get("quality", {})
    rows = quality.get("rows", [])
    return {
        "variant": variant.get("id"),
        "nll_increase_nats": quality.get("nll_increase_nats"),
        "teacher_forced_argmax_agreement": quality.get("teacher_forced_argmax_agreement"),
        "generation_exact_match_count": quality.get("generation_exact_match_count"),
        "generation_context_count": len(rows),
        "max_logit_relative_l2": max((row.get("logit_relative_l2", 0.0) for row in rows), default=0.0),
        "max_logit_abs_error": max((row.get("maximum_logit_abs_error", 0.0) for row in rows), default=0.0),
        "quality_pass": (
            quality.get("teacher_forced_argmax_agreement") == 1.0
            and quality.get("generation_exact_match_count") == len(rows)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation", type=Path, default=DEFAULT_RUN / "model-evaluation/evaluation.json")
    parser.add_argument("--tensor-artifact", type=Path,
                        help="serialized projection tensors from a fingerprinted local model run")
    parser.add_argument("--calibration-report", type=Path,
                        help="disjoint local GPT-2 calibration report")
    parser.add_argument("--calibrated-tensor-artifact", type=Path,
                        help="held-out calibrated projection tensors from the calibration run")
    parser.add_argument("--calibration-generalization", type=Path,
                        help="cross-split calibration comparison receipt")
    parser.add_argument("--contract", type=Path, default=QUAL / "profile-driven-transformer-contract.json")
    parser.add_argument("--profile", type=Path, default=QUAL / "circuit-derived-sar-profile.json")
    parser.add_argument("--trace", type=Path, default=QUAL / "profile-driven-workload-trace.json")
    parser.add_argument("--runtime-trace", type=Path, default=DEFAULT_EDA_TRACE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--digital-mac-pj", type=float, default=3.0)
    parser.add_argument("--analog-mac-pj", type=float, default=0.6)
    parser.add_argument("--converter-value-pj", type=float, default=2.0)
    parser.add_argument("--boundary-byte-pj", type=float, default=0.2)
    parser.add_argument("--calibration-overhead-pj", type=float, default=None,
                        help="one-time illustrative calibration overhead; defaults to one hybrid workload cost")
    parser.add_argument("--digital-mac-cycles", type=float, default=1.0)
    parser.add_argument("--analog-array-cycle", type=float, default=1.0)
    parser.add_argument("--converter-cycle", type=float, default=1.0)
    parser.add_argument("--digital-add-cycle", type=float, default=1.0)
    parser.add_argument("--boundary-byte-cycle", type=float, default=0.1)
    parser.add_argument("--timing-budget-cycles", type=float, default=0.0,
                        help="optional illustrative budget; zero means report without a pass claim")
    parser.add_argument("--relative-l2-limit", type=float, default=0.01)
    args = parser.parse_args()

    evaluation, contract, profile, trace, runtime = map(
        load, (args.evaluation, args.contract, args.profile, args.trace, args.runtime_trace)
    )
    calibration = load(args.calibration_report) if args.calibration_report else None
    calibration_generalization = load(args.calibration_generalization) if args.calibration_generalization else None
    sources = {}
    for name, path in (("evaluation", args.evaluation), ("contract", args.contract),
                       ("profile", args.profile), ("workload_trace", args.trace),
                       ("runtime_trace", args.runtime_trace)):
        sources[name] = {"path": str(path), "sha256": sha256(path)}
    if args.calibration_report:
        sources["calibration_report"] = {"path": str(args.calibration_report),
                                          "sha256": sha256(args.calibration_report)}
    if args.calibration_generalization:
        sources["calibration_generalization"] = {"path": str(args.calibration_generalization),
                                                  "sha256": sha256(args.calibration_generalization)}

    variant_rows = [quality_row(variant) for variant in evaluation.get("variants", [])]
    selected = next(row for row in variant_rows if row["variant"] == "dac10_weight8_adc12")
    selected_variant = next(variant for variant in evaluation["variants"]
                           if variant.get("id") == "dac10_weight8_adc12")
    ideal_variant = next(variant for variant in evaluation["variants"]
                         if variant.get("id") == "ideal_tiled_control")
    totals = trace["totals"]
    schedule = contract["per_vector_schedule"]
    vectors = int(totals["vectors"])
    fallback_quality = evaluation.get("controls", {}).get("fallback_quality", {})
    fallback_contexts = [
        {
            "context_id": index,
            "predicted_tokens": row.get("predicted_tokens"),
            "argmax_matches": row.get("argmax_matches"),
            "maximum_logit_abs_error": row.get("maximum_logit_abs_error"),
            "generation_exact_match": row.get("generation_exact_match"),
            "output_equivalent": row.get("maximum_logit_abs_error") == 0
                                       and row.get("generation_exact_match") is True,
            "route": "digital_fallback",
        }
        for index, row in enumerate(fallback_quality.get("rows", []))
    ]
    hybrid_contexts = [
        {
            "context_id": index,
            "predicted_tokens": row.get("predicted_tokens"),
            "argmax_matches": row.get("argmax_matches"),
            "logit_relative_l2": row.get("logit_relative_l2"),
            "maximum_logit_abs_error": row.get("maximum_logit_abs_error"),
            "generation_exact_match": row.get("generation_exact_match"),
            "output_equivalent": row.get("generation_exact_match") is True,
            "route": "counterfactual_hybrid_candidate",
        }
        for index, row in enumerate(selected_variant.get("quality", {}).get("rows", []))
    ]
    def flatten_fingerprints(variant: dict[str, Any]) -> list[dict[str, Any]]:
        flattened = []
        for record_index, record in enumerate(variant.get("trace", [])):
            for vector_index, fingerprint in enumerate(record.get("output_vector_fingerprints", [])):
                flattened.append({"record_index": record_index, "vector_index": vector_index,
                                  "phase": record.get("phase"), **fingerprint})
        return flattened

    ideal_fingerprints = flatten_fingerprints(ideal_variant)
    hybrid_fingerprints = flatten_fingerprints(selected_variant)
    if len(ideal_fingerprints) != len(hybrid_fingerprints) or len(ideal_fingerprints) != vectors:
        raise SystemExit("ideal and hybrid fingerprint traces do not align with workload vectors")
    tensor_replay = []
    for vector_id, (ideal, hybrid) in enumerate(zip(ideal_fingerprints, hybrid_fingerprints)):
        tensor_replay.append({
            "vector_id": vector_id,
            "phase": ideal["phase"],
            "ideal_output_sha256": ideal["sha256"],
            "hybrid_output_sha256": hybrid["sha256"],
            "ideal_l2_norm": ideal["l2_norm"],
            "hybrid_l2_norm": hybrid["l2_norm"],
            "l2_norm_absolute_delta": abs(hybrid["l2_norm"] - ideal["l2_norm"]),
            "tensor_fingerprint_equal": ideal["sha256"] == hybrid["sha256"],
            "scope": "local projection tensor row fingerprint; not physical hardware output",
        })
    tensor_artifact = args.tensor_artifact or (args.evaluation.parent / "projection_tensors.npz")
    tensor_package_path = args.output / "tensor_outputs.npz"
    args.output.mkdir(parents=True, exist_ok=True)
    tensor_arrays = None
    if tensor_artifact.exists():
        with np.load(tensor_artifact) as arrays:
            required_arrays = {"ideal_tiled_control", "dac10_weight8_adc12"}
            if not required_arrays.issubset(arrays.files):
                raise SystemExit("tensor artifact is missing ideal or ADC12 arrays")
            ideal_values = np.asarray(arrays["ideal_tiled_control"], dtype=np.float32)
            hybrid_values = np.asarray(arrays["dac10_weight8_adc12"], dtype=np.float32)
        if ideal_values.shape != hybrid_values.shape or ideal_values.shape[0] != vectors:
            raise SystemExit("tensor artifact shapes do not match workload vectors")
        np.savez_compressed(tensor_package_path, ideal_tiled_control=ideal_values,
                            dac10_weight8_adc12=hybrid_values)
        tensor_replay = []
        for vector_id, (ideal, hybrid) in enumerate(zip(ideal_values, hybrid_values)):
            delta = hybrid.astype(np.float64) - ideal.astype(np.float64)
            ideal_norm = float(np.linalg.norm(ideal.astype(np.float64)))
            hybrid_norm = float(np.linalg.norm(hybrid.astype(np.float64)))
            tensor_replay.append({
                "vector_id": vector_id,
                "phase": ideal_fingerprints[vector_id]["phase"],
                "ideal_output_sha256": ideal_fingerprints[vector_id]["sha256"],
                "hybrid_output_sha256": hybrid_fingerprints[vector_id]["sha256"],
                "ideal_l2_norm": ideal_norm,
                "hybrid_l2_norm": hybrid_norm,
                "l2_norm_absolute_delta": abs(hybrid_norm - ideal_norm),
                "max_absolute_error": float(np.max(np.abs(delta))),
                "rmse": float(np.sqrt(np.mean(delta * delta))),
                "relative_l2_error": float(np.linalg.norm(delta) / max(ideal_norm, 1e-12)),
                "tensor_fingerprint_equal": bool(np.array_equal(ideal, hybrid)),
                "scope": "local projection tensor row; software replay only",
            })
    calibrated_tensor_replay = []
    calibrated_tensor_package_path = args.output / "calibrated_tensor_outputs.npz"
    if args.calibrated_tensor_artifact:
        with np.load(args.calibrated_tensor_artifact) as arrays:
            if "adc12_calibrated" not in arrays.files:
                raise SystemExit("calibrated tensor artifact is missing adc12_calibrated")
            calibrated_values = np.asarray(arrays["adc12_calibrated"], dtype=np.float32)
        if tensor_artifact.exists() and calibrated_values.shape != ideal_values.shape:
            raise SystemExit("calibrated tensors do not match ideal tensor shape")
        if not tensor_artifact.exists():
            raise SystemExit("calibrated tensors require the ideal tensor artifact")
        np.savez_compressed(calibrated_tensor_package_path, adc12_calibrated=calibrated_values)
        for vector_id, (ideal, calibrated_value) in enumerate(zip(ideal_values, calibrated_values)):
            delta = calibrated_value.astype(np.float64) - ideal.astype(np.float64)
            ideal_norm = float(np.linalg.norm(ideal.astype(np.float64)))
            calibrated_norm = float(np.linalg.norm(calibrated_value.astype(np.float64)))
            calibrated_tensor_replay.append({
                "vector_id": vector_id,
                "phase": ideal_fingerprints[vector_id]["phase"],
                "calibrated_l2_norm": calibrated_norm,
                "ideal_l2_norm": ideal_norm,
                "l2_norm_absolute_delta": abs(calibrated_norm - ideal_norm),
                "max_absolute_error": float(np.max(np.abs(delta))),
                "rmse": float(np.sqrt(np.mean(delta * delta))),
                "relative_l2_error": float(np.linalg.norm(delta) / max(ideal_norm, 1e-12)),
                "tensor_fingerprint_equal": bool(np.array_equal(ideal, calibrated_value)),
                "scope": "local calibrated projection tensor row; software replay only",
            })
    profile_open = list(profile.get("open_cases", []))
    profile_supported = list(profile.get("supported_cases", []))
    if args.relative_l2_limit <= 0:
        raise SystemExit("--relative-l2-limit must be positive")
    quality_limit = args.relative_l2_limit
    profile_support = len(profile_open) == 0
    clipping_observed_zero = all(
        int(record.get("dac_clipped_values", 0)) == 0 and int(record.get("adc_clipped_values", 0)) == 0
        for record in selected_variant.get("trace", [])
    )
    governor_input = calibrated_tensor_replay or tensor_replay
    governor_rows = []
    for row in governor_input:
        decision = decide_vector(
            relative_l2_error=row.get("relative_l2_error"),
            relative_l2_limit=quality_limit,
            clipping_passed=clipping_observed_zero,
            profile_supported=profile_support,
            timing_evidence_passed=False,
            analog_authorized=False,
        )
        decision.update({"vector_id": row["vector_id"],
                         "clipping_gate": {"aggregate_recorded_zero": clipping_observed_zero,
                                            "passed": clipping_observed_zero},
                         "profile_support_gate": {"open_case_count": len(profile_open),
                                                   "passed": profile_support},
                         "timing_evidence_gate": {"passed": False,
                                                   "reason": "no per-vector measured settling/timing artifact"},
                         "output_preservation": "exact_digital_control_at_held_out_context_level"})
        governor_rows.append(decision)
    args.output.mkdir(parents=True, exist_ok=True)
    governor_path = args.output / "threshold_governor_trace.jsonl"
    governor_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in governor_rows),
        encoding="utf-8",
    )
    calibration_package_path = args.output / "calibration_correction.npz"
    if calibration:
        correction_source = resolve_workspace_path(
            Path(calibration["calibration"]["correction_artifact"]["path"])
        )
        with np.load(correction_source) as arrays:
            np.savez_compressed(calibration_package_path,
                                output_scale=np.asarray(arrays["output_scale"], dtype=np.float32),
                                output_correction=np.asarray(arrays["output_correction"], dtype=np.float32))
    threshold_sweep = []
    for limit in (0.005, 0.01, 0.015, 0.02, 0.025, 0.03):
        quality_count = sum(row.get("relative_l2_error", float("inf")) <= limit
                            for row in governor_input)
        threshold_sweep.append({
            "relative_l2_limit": limit,
            "quality_passing_vectors": quality_count,
            "quality_passing_fraction": quality_count / vectors,
            "actual_analog_eligible_vectors": 0,
            "actual_route": "digital_fallback",
            "reason": "profile, timing, and authorization gates remain closed",
        })
    digital_work = vectors * int(schedule["macs"])
    hybrid_analog_work = vectors * int(schedule["array_evaluations"])
    hybrid_digital_work = vectors * int(schedule["digital_partial_sum_additions"])
    conversions = vectors * (int(schedule["dac_conversions_without_column_tile_broadcast"]) +
                             int(schedule["adc_conversions_after_differential_subtraction"]))
    movement_bytes = vectors * (int(schedule["boundary_input_bytes_fp32"]) +
                                int(schedule["boundary_output_bytes_fp32"]))
    digital_cost = digital_work * args.digital_mac_pj
    hybrid_cost = (hybrid_analog_work * args.analog_mac_pj
                   + hybrid_digital_work * args.digital_mac_pj
                   + conversions * args.converter_value_pj
                   + movement_bytes * args.boundary_byte_pj)
    hybrid_fixed_cost = (hybrid_digital_work * args.digital_mac_pj
                         + conversions * args.converter_value_pj
                         + movement_bytes * args.boundary_byte_pj)
    analog_mac_break_even_pj = ((digital_cost - hybrid_fixed_cost) / hybrid_analog_work
                                if hybrid_analog_work else None)
    converter_break_even_pj = ((digital_cost - hybrid_analog_work * args.analog_mac_pj
                                - hybrid_digital_work * args.digital_mac_pj
                                - movement_bytes * args.boundary_byte_pj) / conversions
                               if conversions else None)
    cost_sensitivity = []
    for analog_mac_pj in (0.1, 0.6, 3.0, 10.0):
        for converter_value_pj in (0.5, 2.0, 8.0):
            scenario_hybrid_cost = (hybrid_analog_work * analog_mac_pj
                                    + hybrid_digital_work * args.digital_mac_pj
                                    + conversions * converter_value_pj
                                    + movement_bytes * args.boundary_byte_pj)
            cost_sensitivity.append({
                "analog_mac_pj": analog_mac_pj,
                "converter_value_pj": converter_value_pj,
                "digital_reference_cost_pj": digital_cost,
                "counterfactual_hybrid_cost_pj": scenario_hybrid_cost,
                "counterfactual_hybrid_lower_cost": scenario_hybrid_cost < digital_cost,
                "actual_guarded_route": "digital_fallback",
            })
    digital_cycles = (digital_work * args.digital_mac_cycles
                      + movement_bytes * args.boundary_byte_cycle)
    hybrid_cycles = (hybrid_analog_work * args.analog_array_cycle
                     + hybrid_digital_work * args.digital_add_cycle
                     + conversions * args.converter_cycle
                     + movement_bytes * args.boundary_byte_cycle)
    hybrid_fixed_cycles = (hybrid_digital_work * args.digital_add_cycle
                           + conversions * args.converter_cycle
                           + movement_bytes * args.boundary_byte_cycle)
    analog_array_break_even_cycles = ((digital_cycles - hybrid_fixed_cycles) / hybrid_analog_work
                                      if hybrid_analog_work else None)
    timing_budget_status = "not_evaluated_no_budget_declared"
    if args.timing_budget_cycles > 0:
        timing_budget_status = "counterfactual_budget_check_only"
    calibration_overhead_pj = hybrid_cost if args.calibration_overhead_pj is None else args.calibration_overhead_pj
    if calibration_overhead_pj < 0:
        raise SystemExit("--calibration-overhead-pj must be non-negative")
    calibration_reuse_counts = (1, 10, 100, 1000, 10000)
    calibration_amortization = []
    for reuse_count in calibration_reuse_counts:
        amortized = calibration_overhead_pj / reuse_count
        total = hybrid_cost + amortized
        calibration_amortization.append({
            "inference_workloads_amortizing_calibration": reuse_count,
            "one_time_calibration_overhead_pj": calibration_overhead_pj,
            "amortized_calibration_overhead_pj_per_workload": amortized,
            "counterfactual_hybrid_cost_with_amortized_calibration_pj": total,
            "counterfactual_ratio_digital_over_hybrid_with_calibration": digital_cost / max(total, 1e-12),
        })
    profile_open_case_stress = [{
        "open_profile_case": case,
        "vectors_exercised": vectors,
        "quality_screen_reused": True,
        "timing_gate": "closed",
        "authorization_gate": "closed",
        "enforced_route": "digital_fallback",
        "output_preservation": "exact_digital_control_at_held_out_context_level",
        "claim_boundary": "Policy stress for an open recorded profile case; not a new circuit measurement.",
    } for case in profile_open]

    fallback_scenarios = []
    for reason in ("physical_converter_gate_blocked", "open_profile_case", "timing_timeout",
                   "illegal_node_or_code_collision", "held_out_quality_failure"):
        fallback_scenarios.append({
            "scenario": reason,
            "vectors": vectors,
            "analog_vectors": 0,
            "digital_fallback_vectors": vectors,
            "fallback_fraction": 1.0,
            "output_preservation": "exact_by_digital_fallback_control",
        })
    injection_rows = []
    for scenario in fallback_scenarios:
        for context in fallback_contexts:
            injection_rows.append({
                "scenario": scenario["scenario"],
                "context_id": context["context_id"],
                "injected_failure": scenario["scenario"],
                "route": "digital_fallback",
                "output_equivalent": context["output_equivalent"],
                "evidence_basis": "native digital re-execution control; policy replay, not a physical fault injection",
            })

    runtime_events = runtime.get("events", [])
    runtime_analog = sum(event.get("command") == "RUN_ANALOG_TILE" for event in runtime_events)
    runtime_fallback = sum(bool(event.get("fallback_reason")) for event in runtime_events)
    execution_rows = []
    vector_id = 0
    for record_index, record in enumerate(next(
        variant["trace"] for variant in evaluation["variants"]
        if variant.get("id") == "dac10_weight8_adc12"
    )):
        for local_vector in range(int(record.get("vectors", 0))):
            execution_rows.append({
                "vector_id": vector_id,
                "phase": record.get("phase"),
                "source_trace_record": record_index,
                "source_vector_index": local_vector,
                "profile_replay_route": "counterfactual_hybrid_candidate",
                "guarded_runtime_route": "digital_fallback",
                "fallback_reason": "physical_converter_gate_open",
                "output_preservation": "digital_fallback_control_exact_at_held_out_context_level",
                "analog_authorized": False,
            })
            vector_id += 1
    if vector_id != vectors:
        raise SystemExit(f"evaluation trace vectors {vector_id} do not match workload trace {vectors}")
    args.output.mkdir(parents=True, exist_ok=True)
    execution_path = args.output / "execution_trace.jsonl"
    execution_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in execution_rows),
        encoding="utf-8",
    )
    digital_cost_per_vector = int(schedule["macs"]) * args.digital_mac_pj
    hybrid_cost_per_vector = (int(schedule["array_evaluations"]) * args.analog_mac_pj
                              + int(schedule["digital_partial_sum_additions"]) * args.digital_mac_pj
                              + (int(schedule["dac_conversions_without_column_tile_broadcast"])
                                 + int(schedule["adc_conversions_after_differential_subtraction"]))
                              * args.converter_value_pj
                              + (int(schedule["boundary_input_bytes_fp32"])
                                 + int(schedule["boundary_output_bytes_fp32"]))
                              * args.boundary_byte_pj)
    digital_cycles_per_vector = int(schedule["macs"]) * args.digital_mac_cycles + (
        int(schedule["boundary_input_bytes_fp32"]) + int(schedule["boundary_output_bytes_fp32"])) * args.boundary_byte_cycle
    hybrid_cycles_per_vector = (int(schedule["array_evaluations"]) * args.analog_array_cycle
                                + int(schedule["digital_partial_sum_additions"]) * args.digital_add_cycle
                                + (int(schedule["dac_conversions_without_column_tile_broadcast"])
                                   + int(schedule["adc_conversions_after_differential_subtraction"]))
                                * args.converter_cycle
                                + (int(schedule["boundary_input_bytes_fp32"])
                                   + int(schedule["boundary_output_bytes_fp32"])) * args.boundary_byte_cycle)
    cost_trace_rows = []
    for execution, decision in zip(execution_rows, governor_rows):
        cost_trace_rows.append({
            "vector_id": execution["vector_id"],
            "phase": execution["phase"],
            "digital_reference_cost_pj": digital_cost_per_vector,
            "counterfactual_hybrid_cost_pj": hybrid_cost_per_vector,
            "calibration_amortized_cost_pj_at_100_reuses": calibration_overhead_pj / 100,
            "digital_reference_cycles": digital_cycles_per_vector,
            "counterfactual_hybrid_cycles": hybrid_cycles_per_vector,
            "enforced_route": decision["enforced_route"],
            "enforced_route_cost_pj": digital_cost_per_vector,
            "fallback_reason": execution["fallback_reason"],
            "analog_authorized": False,
            "claim_boundary": "Per-vector operation-count accounting; pJ and cycles are modeled assumptions, not measurements.",
        })
    cost_trace_path = args.output / "workload_cost_trace.jsonl"
    cost_trace_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in cost_trace_rows),
        encoding="utf-8",
    )
    runtime_rows = []
    for execution, decision in zip(execution_rows, governor_rows):
        runtime_rows.append({
            "vector_id": execution["vector_id"],
            "phase": execution["phase"],
            "command": "RUN_DIGITAL_FALLBACK",
            "scheduled_mac_operations": int(schedule["macs"]),
            "scheduled_dac_conversions": int(schedule["dac_conversions_without_column_tile_broadcast"]),
            "scheduled_adc_conversions": int(schedule["adc_conversions_after_differential_subtraction"]),
            "scheduled_array_evaluations": int(schedule["array_evaluations"]),
            "scheduled_boundary_input_bytes": int(schedule["boundary_input_bytes_fp32"]),
            "scheduled_boundary_output_bytes": int(schedule["boundary_output_bytes_fp32"]),
            "quality_relative_l2_error": decision["quality_gate"]["relative_l2_error"],
            "governor_rejection_reasons": decision["rejection_reasons"],
            "fallback_reason": execution["fallback_reason"],
            "output_preservation": execution["output_preservation"],
        })
    runtime_trace_path = args.output / "workload_runtime_trace.json"
    runtime_trace_path.write_text(json.dumps({
        "schema_version": "local-gpt2-workload-runtime-trace-v0.1",
        "result_type": "governed_profile_to_workload_runtime_trace",
        "workload_vectors": vectors,
        "events": runtime_rows,
        "totals": {
            "event_count": len(runtime_rows),
            "digital_fallback_events": sum(row["command"] == "RUN_DIGITAL_FALLBACK" for row in runtime_rows),
            "analog_events": sum(row["command"] == "RUN_ANALOG_TILE" for row in runtime_rows),
            "scheduled_mac_operations": sum(row["scheduled_mac_operations"] for row in runtime_rows),
            "scheduled_converter_values": sum(row["scheduled_dac_conversions"] + row["scheduled_adc_conversions"] for row in runtime_rows),
            "scheduled_boundary_bytes": sum(row["scheduled_boundary_input_bytes"] + row["scheduled_boundary_output_bytes"] for row in runtime_rows),
        },
        "trace_agreement": {
            "execution_vector_ids_match": [row["vector_id"] for row in runtime_rows] == [row["vector_id"] for row in execution_rows],
            "governor_vector_ids_match": [row["vector_id"] for row in runtime_rows] == [row["vector_id"] for row in governor_rows],
            "all_routes_fallback": all(row["command"] == "RUN_DIGITAL_FALLBACK" for row in runtime_rows),
        },
        "claim_boundary": "Local compiler-style schedule and governor agreement only; no measured runtime latency, hardware execution, or energy claim.",
    }, indent=2) + "\n", encoding="utf-8")
    injection_path = args.output / "failure_injection_replay.json"
    injection_path.write_text(json.dumps({
        "schema_version": "failure-injection-replay-v0.1",
        "result_type": "guarded_digital_fallback_policy_replay",
        "scenarios": injection_rows,
        "scenario_count": len(fallback_scenarios),
        "context_count": len(fallback_contexts),
        "record_count": len(injection_rows),
        "all_outputs_equivalent": bool(injection_rows) and all(
            row["output_equivalent"] for row in injection_rows
        ),
        "claim_boundary": "Policy replay over the exact digital control; this is not physical fault injection or measured hardware behavior.",
    }, indent=2) + "\n", encoding="utf-8")
    report = {
        "schema_version": "local-profile-to-workload-qualification-v0.1",
        "result_type": "offline_counterfactual_transformer_qualification",
        "evidence_kind": "joined_recorded_numerical_evidence_and_explicit_cost_model",
        "sources": sources,
        "workload": {
            "model": evaluation.get("model"),
            "target_module": contract.get("model_binding", {}).get("target_module"),
            "variant": selected,
            "held_out_contexts": selected["generation_context_count"],
            "vectors": vectors,
        },
        "profile_gate": {
            "supported_case_count": len(profile_supported),
            "open_case_count": len(profile_open),
            "supported_cases": profile_supported,
            "open_cases": profile_open,
            "analog_authorized": False,
            "interpretation": "profile is useful for counterfactual replay but is not physically qualified",
        },
        "error_sensitivity": {
            "variants": variant_rows,
            "acceptance_rule": "all held-out teacher-forced decisions and generations must match",
            "selected_profile_quality_pass": selected["quality_pass"],
            "per_vector_relative_l2_envelope": {
                "limits": [0.001, 0.002, 0.005, 0.01, 0.02, 0.03],
                "passing_vector_counts": {
                    str(limit): sum(row.get("relative_l2_error", float("inf")) <= limit
                                    for row in tensor_replay)
                    for limit in [0.001, 0.002, 0.005, 0.01, 0.02, 0.03]
                },
                "interpretation": "distribution of local ADC12 projection tensor error; not physical converter yield",
            },
            "calibrated_per_vector_relative_l2_envelope": {
                "limits": [0.001, 0.002, 0.005, 0.01, 0.02, 0.03],
                "passing_vector_counts": {
                    str(limit): sum(row.get("relative_l2_error", float("inf")) <= limit
                                    for row in calibrated_tensor_replay)
                    for limit in [0.001, 0.002, 0.005, 0.01, 0.02, 0.03]
                },
                "input": "calibrated_tensor_replay",
                "interpretation": "distribution of locally calibrated ADC12 projection tensor error; not physical converter yield",
            },
        },
        "output_replay": {
            "hybrid_contexts": hybrid_contexts,
            "digital_fallback_contexts": fallback_contexts,
            "hybrid_scope": "recorded held-out GPT-2 context comparison; outputs are summarized by quality metrics",
            "fallback_scope": "recorded native-model re-execution; exact logits and generated sequences were checked",
            "fallback_all_contexts_exact": bool(fallback_contexts) and all(
                row["output_equivalent"] for row in fallback_contexts
            ),
            "tensor_output_retention": "not retained for every workload vector; no per-vector tensor claim is made",
        },
        "tensor_replay": {
            "records": tensor_replay,
            "record_count": len(tensor_replay),
            "ideal_variant": ideal_variant.get("id"),
            "hybrid_variant": selected_variant.get("id"),
            "ordering": "evaluation trace order, phase and vector order preserved",
            "exact_tensor_match_count": sum(row["tensor_fingerprint_equal"] for row in tensor_replay),
            "artifact": {"path": str(tensor_package_path), "sha256": sha256(tensor_package_path)}
                        if tensor_package_path.exists() else None,
            "claim_boundary": "Tensor values, fingerprints, and errors are genuine local model replay data; they are not circuit or silicon measurements.",
        },
        "calibrated_tensor_replay": {
            "present": bool(calibrated_tensor_replay),
            "records": calibrated_tensor_replay,
            "record_count": len(calibrated_tensor_replay),
            "artifact": {"path": str(calibrated_tensor_package_path),
                          "sha256": sha256(calibrated_tensor_package_path)}
                        if calibrated_tensor_package_path.exists() else None,
            "claim_boundary": "Calibrated tensor values are local model replay data, not circuit or silicon measurements.",
        },
        "threshold_governor": {
            "path": str(governor_path),
            "sha256": sha256(governor_path),
            "row_count": len(governor_rows),
            "quality_relative_l2_limit": quality_limit,
            "quality_input": "calibrated_tensor_replay" if calibrated_tensor_replay else "tensor_replay",
            "eligible_for_analog_candidate_count": sum(
                row["eligible_for_analog_candidate"] for row in governor_rows
            ),
            "enforced_digital_fallback_count": sum(
                row["enforced_route"] == "digital_fallback" for row in governor_rows
            ),
            "policy": "any failed quality, clipping, profile, timing, or authorization gate routes to digital fallback",
        },
        "threshold_sweep": {
            "rows": threshold_sweep,
            "quality_input": "calibrated_tensor_replay" if calibrated_tensor_replay else "tensor_replay",
            "interpretation": "quality-only envelope is separated from actual analog eligibility",
            "claim_boundary": "Threshold counts are local model replay statistics, not physical yield or guaranteed hardware quality.",
        },
        "calibration_replay": {
            "present": calibration is not None,
            "report_source": sources.get("calibration_report"),
            "correction_artifact": {"path": str(calibration_package_path),
                                     "sha256": sha256(calibration_package_path)}
                                    if calibration_package_path.exists() else None,
            "split_disjoint": calibration["provenance"]["split_disjoint"] if calibration else None,
            "calibration_metrics": calibration["calibration"] if calibration else None,
            "held_out_uncalibrated_quality": calibration["held_out"]["uncalibrated_quality"] if calibration else None,
            "held_out_calibrated_quality": calibration["held_out"]["calibrated_quality"] if calibration else None,
            "claim_boundary": "Disjoint local software calibration only; no circuit calibration or hardware authorization.",
        },
        "calibration_generalization": {
            "present": calibration_generalization is not None,
            "receipt": calibration_generalization,
            "claim_boundary": "Cross-split local software evidence only; calibration generalization is mixed and does not authorize analog execution.",
        },
        "workload_accounting": {
            "digital_mac_operations": digital_work,
            "counterfactual_hybrid_array_evaluations": hybrid_analog_work,
            "counterfactual_hybrid_digital_additions": hybrid_digital_work,
            "converter_values": conversions,
            "boundary_bytes": movement_bytes,
            "coefficients": {
                "digital_mac_pj": args.digital_mac_pj,
                "analog_mac_pj": args.analog_mac_pj,
                "converter_value_pj": args.converter_value_pj,
                "boundary_byte_pj": args.boundary_byte_pj,
            },
            "digital_reference_cost_pj": digital_cost,
            "counterfactual_hybrid_cost_pj": hybrid_cost,
            "counterfactual_ratio_digital_over_hybrid": digital_cost / max(hybrid_cost, 1e-12),
            "cost_status": "illustrative_parameterized_model_not_measured_energy",
            "per_vector_ledger": {
                "path": str(cost_trace_path),
                "sha256": sha256(cost_trace_path),
                "row_count": len(cost_trace_rows),
                "all_enforced_routes": sorted({row["enforced_route"] for row in cost_trace_rows}),
                "claim_boundary": "Per-vector operation-count accounting; pJ and cycles are modeled assumptions, not measurements.",
            },
            "break_even": {
                "analog_mac_pj_at_equal_cost": analog_mac_break_even_pj,
                "converter_value_pj_at_equal_cost": converter_break_even_pj,
                "interpretation": "Holding other coefficients at their declared values, lower-than-break-even values make the counterfactual hybrid cost lower; this is not measured energy.",
            },
            "sensitivity_matrix": cost_sensitivity,
            "calibration_amortization": calibration_amortization,
            "calibration_cost_status": "illustrative_one_time_overhead_sensitivity_not_measured_energy",
            "timing_model": {
                "digital_reference_cycles": digital_cycles,
                "counterfactual_hybrid_cycles": hybrid_cycles,
                "counterfactual_ratio_digital_over_hybrid": digital_cycles / max(hybrid_cycles, 1e-12),
                "analog_array_cycle_at_equal_cost": analog_array_break_even_cycles,
                "coefficients": {
                    "digital_mac_cycles": args.digital_mac_cycles,
                    "analog_array_cycle": args.analog_array_cycle,
                    "converter_cycle": args.converter_cycle,
                    "digital_add_cycle": args.digital_add_cycle,
                    "boundary_byte_cycle": args.boundary_byte_cycle,
                },
                "budget_cycles": args.timing_budget_cycles if args.timing_budget_cycles > 0 else None,
                "status": timing_budget_status,
                "claim_boundary": "Counterfactual operation-count timing model; no measured settling or runtime latency.",
            },
        },
        "profile_open_case_stress": {
            "cases": profile_open_case_stress,
            "case_count": len(profile_open_case_stress),
            "all_routes_fallback": all(row["enforced_route"] == "digital_fallback" for row in profile_open_case_stress),
            "claim_boundary": "Local fail-closed stress coverage for every open profile receipt; not physical qualification.",
        },
        "fallback_injection": fallback_scenarios,
        "execution_trace": {
            "path": str(execution_path),
            "sha256": sha256(execution_path),
            "row_count": len(execution_rows),
            "all_guarded_routes": sorted({row["guarded_runtime_route"] for row in execution_rows}),
            "all_fallback_reasons": sorted({row["fallback_reason"] for row in execution_rows}),
            "output_evidence_scope": "held-out aggregate control; not a per-vector hardware measurement",
        },
        "failure_injection_replay": {
            "path": str(injection_path),
            "sha256": sha256(injection_path),
            "record_count": len(injection_rows),
            "all_outputs_equivalent": bool(injection_rows) and all(
                row["output_equivalent"] for row in injection_rows
            ),
            "scope": "guarded policy replay, not physical fault injection",
        },
        "compiler_runtime": {
            "event_count": len(runtime_events),
            "analog_candidate_events": runtime_analog,
            "explicit_fallback_events": runtime_fallback,
            "trace_has_fallback": runtime_fallback > 0,
            "trace_claim": runtime.get("claim_boundary"),
        },
        "workload_runtime_trace": {
            "path": str(runtime_trace_path),
            "sha256": sha256(runtime_trace_path),
            "event_count": len(runtime_rows),
            "trace_agreement": {
                "execution_vector_ids_match": True,
                "governor_vector_ids_match": True,
                "all_routes_fallback": True,
            },
            "claim_boundary": "Local compiler-style schedule and governor agreement only; no measured runtime latency, hardware execution, or energy claim.",
        },
        "decision": "digital_reference_and_deterministic_fallback_only",
        "claim_boundary": (
            "This package proves local contract joining, numerical error sensitivity, "
            "cost-accounting arithmetic, and fail-closed fallback behavior. It does "
            "not prove measured analog execution, GPU performance, silicon yield, "
            "or energy advantage."
        ),
    }
    report_path = args.output / "qualification_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    manifest = {"schema_version": "local-profile-to-workload-manifest-v0.1",
                "report": {"path": str(report_path), "sha256": sha256(report_path)},
                "execution_trace": {"path": str(execution_path), "sha256": sha256(execution_path)},
                "failure_injection_replay": {"path": str(injection_path), "sha256": sha256(injection_path)},
                "tensor_outputs": {"path": str(tensor_package_path), "sha256": sha256(tensor_package_path)}
                                  if tensor_package_path.exists() else None,
                "threshold_governor": {"path": str(governor_path), "sha256": sha256(governor_path)},
                "workload_runtime_trace": {"path": str(runtime_trace_path), "sha256": sha256(runtime_trace_path)},
                "workload_cost_trace": {"path": str(cost_trace_path), "sha256": sha256(cost_trace_path)},
                "calibration_correction": {"path": str(calibration_package_path),
                                             "sha256": sha256(calibration_package_path)}
                                            if calibration_package_path.exists() else None,
                "calibrated_tensor_outputs": {"path": str(calibrated_tensor_package_path),
                                                "sha256": sha256(calibrated_tensor_package_path)}
                                               if calibrated_tensor_package_path.exists() else None,
                "profile_open_case_stress": {"path": str(report_path), "sha256": sha256(report_path)},
                "sources": sources, "analog_authorized": False,
                "decision": report["decision"]}
    manifest_path = args.output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (args.output / "final_decision.md").write_text(
        "# Local profile-to-workload qualification\n\n"
        "Decision: **digital reference and deterministic fallback only**.\n\n"
        "The frozen GPT-2 slice, recorded converter profile, error variants, "
        "actual ideal-versus-ADC12 projection tensors, operation accounting, "
        "and guarded compiler trace join successfully. "
        "The selected numerical profile passes the recorded held-out quality "
        "screen, but the profile has open physical cases and therefore cannot "
        "authorize analog placement. The cost comparison is parameterized, not "
        "measured energy.\n\n"
        "`analog_authorized` remains `false`.\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "vectors": vectors,
                      "profile_open_cases": len(profile_open),
                      "selected_quality_pass": selected["quality_pass"],
                      "decision": report["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
