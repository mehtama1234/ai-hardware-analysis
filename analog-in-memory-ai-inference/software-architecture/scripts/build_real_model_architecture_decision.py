#!/usr/bin/env python3
"""Build the claim-safe architecture decision from measured GPT-2 evidence."""

from __future__ import annotations

from typing import Any


def build(
    verdict: dict[str, Any],
    workload_contract: dict[str, Any],
    physical_gate: dict[str, Any],
    sdpa: dict[str, Any] | None = None,
) -> dict[str, Any]:
    comparison = verdict.get("measured_comparison", {})
    analog_allowed = bool(physical_gate.get("analog_allowed_for_physical_claim", False))
    candidate_promoted = verdict.get("decision") == "device_resident_candidate_accepted_for_recorded_scope"
    diagnostic = verdict.get("diagnostic_finding")
    primary_next = (
        "retain native digital serving and target attention math/launch efficiency; page packing was not latency-dominant in the direct-K/V control"
        if diagnostic == "page_packing_is_not_latency_dominant_in_this_trace"
        else "retain native digital serving and profile the remaining CUDA page-kernel overhead only if runtime improvement is strategically valuable"
    )
    if verdict.get("measured_comparison", {}).get("device_over_native_latency_ratio", 0) > 1.2:
        primary_next = "retain native digital attention as the production baseline; do not spend further architecture effort on this custom paged/persistent path without a materially better kernel/backend"
    return {
        "schema_version": "real-model-architecture-decision-v0.1",
        "decision": "native_digital_serving_baseline_with_cuda_optimization_candidate",
        "model": verdict.get("model", workload_contract.get("model", {})),
        "device_evidence": {
            "device": verdict.get("device"),
            "evidence_kind": verdict.get("evidence_kind"),
            "output_parity": verdict.get("correctness", {}).get("output_parity"),
            "arrival_trace_groups": verdict.get("correctness", {}).get("request_groups", []),
            "cancelled_request_indices": verdict.get("correctness", {}).get("cancelled_request_indices", []),
        },
        "measured_runtime_decision": {
            "native_scheduled_is_authoritative_baseline": not candidate_promoted,
            "cuda_paged_candidate_promoted": candidate_promoted,
            "candidate_latency_ratio_to_native": comparison.get("device_over_native_latency_ratio"),
            "candidate_energy_ratio_to_native": comparison.get("device_over_native_energy_ratio"),
            "candidate_throughput_speedup_vs_independent": comparison.get("throughput_speedup_vs_independent_singles"),
            "reason": verdict.get("recommendation"),
        },
        "native_backend_comparison": {
            "status": "measured_t4_attached" if sdpa else "not_measured",
            "decision": sdpa.get("decision") if sdpa else None,
            "output_parity": sdpa.get("result", {}).get("output_parity") if sdpa else None,
            "sdpa_over_eager_latency_ratio": sdpa.get("result", {}).get("sdpa_over_eager_latency_ratio") if sdpa else None,
            "baseline": "native_eager" if not sdpa or sdpa.get("decision") == "native_sdpa_backend_not_proven_better" else "native_sdpa",
        },
        "execution_placement": {
            "prefill": "native digital GPU/runtime",
            "autoregressive_decode": "native scheduled digital runtime",
            "attention_and_KV_cache": "digital GPU memory and CUDA runtime; paged candidate remains experimental",
            "batching_cancellation_and_admission": "digital scheduler",
            "conversion_and_fallback": "digital control path",
            "analog_regions": [],
        },
        "hardware_contract": {
            "source_decision": workload_contract.get("decision"),
            "digital_required": workload_contract.get("placement_policy", {}).get("digital_required", []),
            "runtime_optimization_target": workload_contract.get("hardware_requirements", {}).get("runtime_optimization_target"),
            "measured_peak_memory_mb": comparison.get("device_peak_memory_mb"),
        },
        "evidence_gates": {
            "real_model_t4_parity": "passed" if verdict.get("correctness", {}).get("output_parity") else "failed",
            "bounded_arrival_trace": "passed" if verdict.get("correctness", {}).get("request_groups") else "missing",
            "native_baseline_competitiveness": "passed" if candidate_promoted else "not_passed",
            "physical_converter_gate": "passed" if analog_allowed else "blocked",
            "analog_per_tile_accuracy_power": "required_before_any_analog_placement",
            "silicon_or_board_measurement": "not_available_and_not_claimed",
        },
        "next_execution": {
            "primary": primary_next,
            "hardware": "use the measured decode/KV movement contract to size digital memory and scheduler resources; target fused append-plus-attention execution and lower persistent-cache launch overhead before considering any accelerator placement",
            "analog": "do not place analog hardware until extracted converter area, post-layout break-even, per-tile accuracy, and synchronized power evidence pass",
        },
        "claim_boundary": "A bounded real GPT-2/Tesla-T4 architecture decision; it is not a silicon result, analog benefit claim, production serving guarantee, or isolated energy-per-token measurement.",
    }
