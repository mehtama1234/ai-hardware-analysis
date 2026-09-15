#!/usr/bin/env python3
"""Derive a claim-safe hardware contract from the measured Colab GPT-2 run."""

from __future__ import annotations

from typing import Any


def _slope(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    return sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denominator if denominator else None


def build(
    characterization: dict[str, Any],
    extended: dict[str, Any],
    physical_gate: dict[str, Any],
    serving_verdict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    phase_rows = []
    for row in characterization.get("rows", []):
        cached = row.get("cached", {})
        total = float(cached.get("wall_time_ms_median", 0.0))
        decode = float(cached.get("last_decode_ms", 0.0))
        phase_rows.append({
            "batch_size": row.get("batch_size"),
            "decode_fraction": decode / total if total else None,
            "prefill_ms": cached.get("last_prefill_ms"),
            "decode_ms": decode,
            "peak_memory_mb": cached.get("peak_memory_mb_max"),
        })
    contexts = extended.get("context_sweep", [])
    context_tokens = [float(row["prompt_token_count"]) for row in contexts]
    context_latency = [float(row["cached_total_ms"]["median_ms"]) for row in contexts]
    context_memory = [float(row["peak_memory_mb"]) for row in contexts]
    profiler = extended.get("operator_data_movement_profile", {})
    max_memory = max(context_memory) if context_memory else None
    measured_serving = None
    if serving_verdict:
        measured_serving = {
            "decision": serving_verdict.get("decision"),
            "correctness": serving_verdict.get("correctness"),
            "comparison": serving_verdict.get("measured_comparison"),
            "recommendation": serving_verdict.get("recommendation"),
            "claim_boundary": serving_verdict.get("claim_boundary"),
        }
    optimization_target = "persistent per-layer K/V page cache with append-only token updates; eliminate full-history repack on every one-token decode call, then require exact parity and candidate latency no worse than native scheduled decode"
    if serving_verdict and serving_verdict.get("measured_comparison", {}).get("candidate_variant") == "persistent_append_only":
        optimization_target = "reduce fused append-plus-attention runtime/kernel overhead; the persistent cache is functionally correct but remains slower and higher-energy than native on the repeated T4 trace"
        if serving_verdict.get("measured_comparison", {}).get("native_scheduled_wall_time_ms_median", 0) > 0 and serving_verdict.get("measured_comparison", {}).get("device_resident_scheduled_wall_time_ms_median", 0) / serving_verdict.get("measured_comparison", {}).get("native_scheduled_wall_time_ms_median", 1) > 1.2:
            optimization_target = "do not promote the custom paged/persistent path for this GPT-2/T4 workload; retain the native digital attention baseline and require a materially better kernel/backend before reopening the candidate"
    elif serving_verdict and serving_verdict.get("diagnostic_finding") == "page_packing_is_not_latency_dominant_in_this_trace":
        optimization_target = "attention math and launch efficiency after persistent per-layer K/V append caching; direct-K/V control was slower than the page-packed candidate in the same bounded trace"
    # These are the canonical GPT-2 configuration dimensions for the imported
    # pinned model revision. They are workload denominators, not silicon claims.
    layers, heads, head_dim = 12, 12, 64
    kv_elements_per_token = layers * heads * head_dim * 2
    model_parameters = int(characterization.get("model_profile", {}).get("parameter_count", 0))
    return {
        "schema_version": "real-model-workload-hardware-contract-v0.1",
        "evidence_kind": "derived_from_measured_gpu",
        "model": characterization.get("model_profile", {}),
        "device": {"name": extended.get("device_name"), "runtime": extended.get("runtime", {})},
        "measured_workload": {
            "phase_rows": phase_rows,
            "context_rows": contexts,
            "context_latency_slope_ms_per_token": _slope(context_tokens, context_latency),
            "context_memory_slope_mb_per_token": _slope(context_tokens, context_memory),
            "maximum_recorded_peak_memory_mb": max_memory,
            "tail_latency": extended.get("tail_latency"),
            "concurrency": extended.get("concurrency", []),
            "power_scope": extended.get("protocol", {}).get("power"),
            "arrival_trace_serving_verdict": measured_serving,
        },
        "derived_digital_denominators": {
            "source": "canonical GPT-2 configuration for the pinned openai-community/gpt2 revision",
            "transformer_layers": layers,
            "attention_heads": heads,
            "head_dimension": head_dim,
            "parameter_count": model_parameters,
            "KV_elements_per_token_all_layers": kv_elements_per_token,
            "KV_bytes_per_token_all_layers_fp16": kv_elements_per_token * 2,
            "KV_bytes_per_token_all_layers_fp32": kv_elements_per_token * 4,
            "single_query_attention_flops_per_history_token_all_layers": 4 * layers * heads * head_dim,
            "model_weight_bytes_fp16": model_parameters * 2,
            "model_weight_bytes_fp32": model_parameters * 4,
            "interpretation": "Use these values to size digital KV/model memory and arithmetic; they do not estimate achieved bandwidth, latency, energy, or analog benefit.",
        },
        "operator_hotspots": profiler.get("top_operators", [])[:10],
        "hardware_requirements": {
            "priority": "decode_first",
            "memory": "digital_KV_and_model_memory; capacity must cover the recorded peak plus deployment headroom",
            "compute": "optimize repeated matrix/vector work represented by the measured CUDA profiler rows",
            "runtime_optimization_target": optimization_target,
            "diagnostic_finding": serving_verdict.get("diagnostic_finding") if serving_verdict else "not_measured",
            "scheduler": "retain digital admission, batching, cancellation, and tail-latency control",
            "power": "use the protocol-scoped NVML sample only as a baseline; do not convert it to per-token energy",
        },
        "placement_policy": {
            "digital_required": ["autoregressive_decode_control", "KV_cache", "attention", "batch_scheduler", "conversion_and_fallback"],
            "analog_candidates": [],
            "analog_status": "deferred_until_converter_and_per_tile_accuracy/power evidence pass",
            "physical_gate_status": physical_gate.get("status"),
        },
        "decision": "pursue_decode_first_digital_runtime_optimization_before_analog_placement",
        "serving_decision": {
            "status": "measured_arrival_trace_attached" if measured_serving else "characterization_only",
            "candidate_decision": measured_serving.get("decision") if measured_serving else None,
            "native_baseline_remains_authoritative": bool(measured_serving and measured_serving.get("decision") == "device_resident_candidate_not_ready_for_runtime_promotion"),
        },
        "claim_boundary": {
            "allowed": "Use this contract to prioritize runtime, memory, and compiler work for the measured GPT-2/Tesla-T4 scope.",
            "refused": "General model scaling, silicon performance, analog speedup, or per-token energy derived from this run.",
        },
    }
