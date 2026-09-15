#!/usr/bin/env python3
"""Derive a bounded decision from real-model serving evidence."""

from __future__ import annotations

from typing import Any


def build_end_to_end_serving_verdict(
    arrival_load: dict[str, Any],
    arrival_stress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive the bounded T4 serving verdict from an accepted arrival trace."""
    result = arrival_load.get("result", {})
    native = result.get("native_scheduled", {})
    device = result.get("device_resident_scheduled", {})
    native_ms = float(native.get("wall_time_ms_median", 0.0))
    device_ms = float(device.get("wall_time_ms_median", 0.0))
    native_energy = native.get("power", {}).get("integrated_energy_j")
    device_energy = device.get("power", {}).get("integrated_energy_j")
    persistent = result.get("device_persistent_scheduled", {})
    candidate = persistent if persistent else device
    candidate_parity = result.get("persistent_output_parity") if persistent else result.get("output_parity")
    candidate_ms = float(candidate.get("wall_time_ms_median", device_ms))
    candidate_energy = candidate.get("power", {}).get("integrated_energy_j")
    direct = result.get("device_direct_scheduled", {})
    direct_ms = direct.get("wall_time_ms_median")
    latency_ratio = candidate_ms / native_ms if native_ms else None
    energy_ratio = (
        float(candidate_energy) / float(native_energy)
        if native_energy is not None and candidate_energy is not None and float(native_energy)
        else None
    )
    parity = bool(candidate_parity)
    if not parity:
        decision = "candidate_rejected_for_output_mismatch"
        recommendation = "retain_native_runtime_until_exact_parity_is_restored"
    elif latency_ratio is not None and latency_ratio <= 1.0 and (energy_ratio is None or energy_ratio <= 1.0):
        decision = "device_resident_candidate_accepted_for_recorded_scope"
        recommendation = "promote_device_resident_decode_to_longer_repeated_load_validation"
    else:
        decision = "device_resident_candidate_not_ready_for_runtime_promotion"
        recommendation = "retain_native_scheduled_decode_and_target_kernel_or_allocator_overhead"
    return {
        "schema_version": "real-model-end-to-end-serving-verdict-v0.1",
        "decision": decision,
        "model": arrival_load.get("model_profile", {}),
        "device": arrival_load.get("device_name"),
        "evidence_kind": arrival_load.get("evidence_kind"),
        "correctness": {
            "output_parity": parity,
            "cancelled_request_indices": result.get("cancelled_request_indices", []),
            "request_groups": result.get("groups", []),
        },
        "measured_comparison": {
            "native_scheduled_wall_time_ms_median": native_ms,
            "device_resident_scheduled_wall_time_ms_median": candidate_ms,
            "native_scheduled_wall_time_ms_samples": native.get("wall_time_ms_samples", []),
            "device_resident_scheduled_wall_time_ms_samples": candidate.get("wall_time_ms_samples", []),
            "direct_control_wall_time_ms_samples": direct.get("wall_time_ms_samples", []),
            "device_over_native_latency_ratio": latency_ratio,
            "throughput_speedup_vs_independent_singles": result.get("throughput_speedup"),
            "persistent_throughput_speedup_vs_independent_singles": result.get("persistent_throughput_speedup"),
            "native_scheduled_energy_j": native_energy,
            "device_resident_scheduled_energy_j": candidate_energy,
            "device_over_native_energy_ratio": energy_ratio,
            "native_peak_memory_mb": native.get("peak_memory_allocated_mb"),
            "device_peak_memory_mb": candidate.get("peak_memory_allocated_mb"),
            "direct_control_wall_time_ms_median": direct_ms,
            "direct_control_output_parity": result.get("direct_output_parity"),
            "paged_over_direct_latency_ratio": (device_ms / float(direct_ms)) if direct_ms else None,
            "page_packing_is_latency_dominant": bool(direct_ms and candidate_ms > float(direct_ms)),
            "candidate_variant": "persistent_append_only" if persistent else "workspace_reuse",
            "energy_claim_scope": candidate.get("power", {}).get("scope"),
        },
        "diagnostic_finding": (
            "page_packing_is_not_latency_dominant_in_this_trace"
            if direct_ms and candidate_ms <= float(direct_ms)
            else "page_packing_or_workspace_path_remains_a_candidate_overhead"
            if direct_ms
            else "direct_control_not_measured"
        ),
        "recommendation": recommendation,
        "architecture_implication": {
            "serving_path": "digital_native_or_fused_cuda_runtime",
            "analog_placement": "blocked_by_physical_converter_gate",
            "why": "The measured candidate is functionally correct but not yet faster or lower-energy than the native scheduled baseline at this T4 protocol; the result identifies a runtime optimization target, not an analog benefit claim.",
        },
        "stress_evidence": {
            "attached": arrival_stress is not None,
            "output_parity": arrival_stress.get("result", {}).get("output_parity") if arrival_stress else None,
            "peak_memory_mb": arrival_stress.get("result", {}).get("device_resident_scheduled", {}).get("peak_memory_allocated_mb") if arrival_stress else None,
        },
        "claim_boundary": "Bounded real GPT-2 arrival-trace comparison on a Tesla T4; not production continuous batching, silicon performance, analog speedup, or isolated energy-per-token.",
    }


def build_decision(
    serving: dict[str, Any],
    characterization: dict[str, Any] | None = None,
    extended: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rows = serving.get("rows", [])
    parity = all(row.get("output_parity", False) for row in rows) if rows else False
    ratios = [float(row["cache_speedup_ratio"]) for row in rows if "cache_speedup_ratio" in row]
    if not rows:
        decision = "insufficient_evidence"
    elif not parity:
        decision = "candidate_rejected_for_output_mismatch"
    elif serving.get("evidence_kind") != "measured_gpu":
        decision = "hardware_measurement_pending"
    elif ratios and all(ratio > 1.0 for ratio in ratios):
        decision = "cached_candidate_improves_measured_scope"
    else:
        decision = "cached_candidate_not_proven_better"
    measured_bottleneck = {
        "status": "comparison_only",
        "finding": "end_to_end_scope_only; prefill_decode_breakdown_not_available",
    }
    if characterization and characterization.get("rows"):
        phase_rows = []
        for row in characterization["rows"]:
            cached = row.get("cached", {})
            total = float(cached.get("wall_time_ms_median", 0.0))
            decode = float(cached.get("last_decode_ms", 0.0))
            if total > 0:
                phase_rows.append({
                    "batch_size": row.get("batch_size"),
                    "prefill_ms": float(cached.get("last_prefill_ms", 0.0)),
                    "decode_ms": decode,
                    "decode_fraction": decode / total,
                    "kv_peak_memory_mb": cached.get("peak_memory_mb_max"),
                })
        if phase_rows:
            dominant = max(phase_rows, key=lambda item: item["decode_fraction"])
            measured_bottleneck = {
                "status": "measured_gpu_characterization",
                "finding": "autoregressive_decode_dominates_recorded_cached_scope",
                "dominant_batch_size": dominant["batch_size"],
                "max_decode_fraction": dominant["decode_fraction"],
                "phase_rows": phase_rows,
                "interpretation": "Bounded GPT-2/Tesla-T4 finding; not a general transformer or silicon claim.",
            }
    extended_findings = None
    if extended:
        power = extended.get("protocol", {}).get("power", {})
        extended_findings = {
            "context_rows": len(extended.get("context_sweep", [])),
            "context_token_counts": [row.get("prompt_token_count") for row in extended.get("context_sweep", [])],
            "context_median_latency_ms": [row.get("cached_total_ms", {}).get("median_ms") for row in extended.get("context_sweep", [])],
            "context_peak_memory_mb": [row.get("peak_memory_mb") for row in extended.get("context_sweep", [])],
            "tail_p95_ms": extended.get("tail_latency", {}).get("latency", {}).get("p95_ms"),
            "concurrency": extended.get("concurrency", []),
            "operator_profile_status": extended.get("operator_data_movement_profile", {}).get("status"),
            "power": {
                "status": power.get("status"),
                "average_power_w": power.get("average_power_w"),
                "peak_power_w": power.get("peak_power_w"),
                "integrated_energy_j": power.get("integrated_energy_j"),
                "scope": power.get("scope"),
            },
        }
    return {
        "schema_version": "real-model-inference-decision-v0.1",
        "decision": decision,
        "model": serving.get("model_profile", {}),
        "evidence_kind": serving.get("evidence_kind"),
        "device": serving.get("device"),
        "workload_count": len(rows),
        "output_parity": parity,
        "cache_speedup_ratios_uncached_over_cached": ratios,
        "measured_bottleneck": measured_bottleneck,
        "extended_measurements": extended_findings,
        "interpretation": {
            "allowed": "The cached/uncached candidate comparison at the recorded device, workload, and timing scope.",
            "refused": "General serving superiority, measured energy savings, analog benefit, and production readiness.",
        },
        "next_required_measurements": [
            "Repeat the Colab protocol across longer contexts, concurrency, and tail-latency samples.",
            "Add an operator and data-movement breakdown for the same real GPT-2 workload.",
            "Add synchronized power/thermal samples before making an energy claim.",
        ],
    }
