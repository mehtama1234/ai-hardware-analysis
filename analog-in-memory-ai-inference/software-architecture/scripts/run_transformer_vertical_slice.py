#!/usr/bin/env python3
"""Build the complete software transformer-to-chip vertical-slice package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from benchmark_tiny_causal_lm import run_benchmark
from build_transformer_execution_contract import build_contract
from import_attention_calibration_profile import import_profile
from import_physical_converter_gate import import_gate
from import_real_model_inference_evidence import validate as import_real_model_evidence
from build_real_model_decision import build_decision, build_end_to_end_serving_verdict
from build_real_model_hybrid_cost_bridge import build as build_hybrid_cost_bridge
from build_real_model_workload_hardware_contract import build as build_workload_hardware_contract
from build_real_model_architecture_decision import build as build_real_model_architecture_decision
from run_tiny_causal_lm_decode import load_gate, run as run_tiny_decode
from run_tiny_causal_lm_reliability_sweep import run_sweep
from run_transformer_decode_comparison import run_decode
from run_transformer_output_comparison import run_comparison


ROOT = Path(__file__).resolve().parents[1]
MLP_MODEL = ROOT / "samples" / "deep-transformer-mlp-stack.onnx"
ATTENTION_MODEL = ROOT / "samples" / "attention-block.onnx"
TINY_MODEL = ROOT / "samples" / "tiny-causal-lm.onnx"
PHYSICAL_GATE = ROOT.parent.parent / "analog-digital-chip-design-eda" / "evidence" / "aimc-simulator-adapters" / "analog-converter-physical-cell-gate.json"
CALIBRATED_PROFILE = ROOT.parent.parent / "analog-digital-chip-design-eda" / "evidence" / "aimc-simulator-adapters" / "crosssim-calibrated-attention-block-analog-error-simulation.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(output: Path, name: str, payload: dict[str, Any]) -> str:
    path = output / name
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path.name


def add_contract_files(output: Path, prefix: str, package: dict[str, Any]) -> list[str]:
    names = []
    for name, payload in package.items():
        names.append(write_json(output, f"{prefix}_{name}.json", payload))
    return names


def run_vertical_slice(
    output: Path,
    include_reliability: bool = True,
    real_model_evidence: Path | None = None,
    real_model_intake: Path | None = None,
    real_model_serving_comparison: Path | None = None,
    real_model_serving_characterization: Path | None = None,
    real_model_serving_extended_characterization: Path | None = None,
    real_model_candidate_comparison: Path | None = None,
    real_model_microbatch_candidate: Path | None = None,
    real_model_continuous_microbatch: Path | None = None,
    real_model_paged_cache_adapter: Path | None = None,
    real_model_paged_attention_kernel: Path | None = None,
    real_model_fused_paged_decode: Path | None = None,
    real_model_device_resident_paged_decode: Path | None = None,
    real_model_device_resident_microbatch: Path | None = None,
    real_model_device_resident_arrival_load: Path | None = None,
    real_model_device_resident_arrival_stress: Path | None = None,
    real_model_sdpa_backend: Path | None = None,
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    physical_gate = load_gate(PHYSICAL_GATE) if PHYSICAL_GATE.exists() else None
    artifacts = []
    physical_gate_audit = None
    if PHYSICAL_GATE.exists():
        physical_gate_audit = import_gate(PHYSICAL_GATE)
        artifacts.append(write_json(output, "physical_converter_gate_import.json", physical_gate_audit))

    real_model_import = None
    if real_model_evidence is not None:
        real_model_import = import_real_model_evidence(real_model_evidence)
        artifacts.append(write_json(output, "real_model_inference_evidence_import.json", real_model_import))

    real_model_intake_payload = None
    if real_model_intake is not None:
        real_model_intake_payload = json.loads(real_model_intake.read_text(encoding="utf-8"))
        real_model_intake_payload["source"] = str(real_model_intake)
        real_model_intake_payload["source_sha256"] = sha256(real_model_intake)
        artifacts.append(write_json(output, "real_model_intake.json", real_model_intake_payload))

    real_model_serving_payload = None
    if real_model_serving_comparison is not None:
        real_model_serving_payload = json.loads(real_model_serving_comparison.read_text(encoding="utf-8"))
        real_model_serving_payload["source"] = str(real_model_serving_comparison)
        real_model_serving_payload["source_sha256"] = sha256(real_model_serving_comparison)
        artifacts.append(write_json(output, "real_model_serving_comparison.json", real_model_serving_payload))
        artifacts.append(write_json(output, "real_model_decision.json", build_decision(real_model_serving_payload)))

    real_model_extended_payload = None
    real_model_characterization_payload = None
    if real_model_serving_characterization is not None:
        real_model_characterization_payload = json.loads(real_model_serving_characterization.read_text(encoding="utf-8"))
        real_model_characterization_payload["source"] = str(real_model_serving_characterization)
        real_model_characterization_payload["source_sha256"] = sha256(real_model_serving_characterization)
        artifacts.append(write_json(output, "real_model_serving_characterization.json", real_model_characterization_payload))
        artifacts.append(write_json(output, "real_model_serving_characterization_import.json", import_real_model_evidence(real_model_serving_characterization)))
        if real_model_serving_payload is not None:
            artifacts.append(write_json(output, "real_model_decision.json", build_decision(real_model_serving_payload, real_model_characterization_payload, real_model_extended_payload)))

    if real_model_serving_extended_characterization is not None:
        real_model_extended_payload = json.loads(real_model_serving_extended_characterization.read_text(encoding="utf-8"))
        real_model_extended_payload["source"] = str(real_model_serving_extended_characterization)
        real_model_extended_payload["source_sha256"] = sha256(real_model_serving_extended_characterization)
        artifacts.append(write_json(output, "real_model_serving_extended_characterization.json", real_model_extended_payload))
        if real_model_serving_payload is not None:
            artifacts.append(write_json(output, "real_model_decision.json", build_decision(real_model_serving_payload, real_model_characterization_payload, real_model_extended_payload)))

    real_model_candidate_payload = None
    if real_model_candidate_comparison is not None:
        real_model_candidate_payload = json.loads(real_model_candidate_comparison.read_text(encoding="utf-8"))
        real_model_candidate_payload["source"] = str(real_model_candidate_comparison)
        real_model_candidate_payload["source_sha256"] = sha256(real_model_candidate_comparison)
        artifacts.append(write_json(output, "real_model_candidate_comparison.json", real_model_candidate_payload))

    real_model_microbatch_payload = None
    if real_model_microbatch_candidate is not None:
        real_model_microbatch_payload = json.loads(real_model_microbatch_candidate.read_text(encoding="utf-8"))
        real_model_microbatch_payload["source"] = str(real_model_microbatch_candidate)
        real_model_microbatch_payload["source_sha256"] = sha256(real_model_microbatch_candidate)
        artifacts.append(write_json(output, "real_model_microbatch_candidate.json", real_model_microbatch_payload))

    real_model_continuous_payload = None
    if real_model_continuous_microbatch is not None:
        real_model_continuous_payload = json.loads(real_model_continuous_microbatch.read_text(encoding="utf-8"))
        real_model_continuous_payload["source"] = str(real_model_continuous_microbatch)
        real_model_continuous_payload["source_sha256"] = sha256(real_model_continuous_microbatch)
        artifacts.append(write_json(output, "real_model_continuous_microbatch.json", real_model_continuous_payload))

    real_model_paged_payload = None
    if real_model_paged_cache_adapter is not None:
        real_model_paged_payload = json.loads(real_model_paged_cache_adapter.read_text(encoding="utf-8"))
        real_model_paged_payload["source"] = str(real_model_paged_cache_adapter)
        real_model_paged_payload["source_sha256"] = sha256(real_model_paged_cache_adapter)
        artifacts.append(write_json(output, "real_model_paged_cache_adapter.json", real_model_paged_payload))

    real_model_paged_kernel_payload = None
    if real_model_paged_attention_kernel is not None:
        real_model_paged_kernel_payload = json.loads(real_model_paged_attention_kernel.read_text(encoding="utf-8"))
        real_model_paged_kernel_payload["source"] = str(real_model_paged_attention_kernel)
        real_model_paged_kernel_payload["source_sha256"] = sha256(real_model_paged_attention_kernel)
        artifacts.append(write_json(output, "real_model_paged_attention_kernel.json", real_model_paged_kernel_payload))

    real_model_fused_paged_payload = None
    if real_model_fused_paged_decode is not None:
        real_model_fused_paged_payload = json.loads(real_model_fused_paged_decode.read_text(encoding="utf-8"))
        real_model_fused_paged_payload["source"] = str(real_model_fused_paged_decode)
        real_model_fused_paged_payload["source_sha256"] = sha256(real_model_fused_paged_decode)
        artifacts.append(write_json(output, "real_model_fused_paged_decode.json", real_model_fused_paged_payload))

    real_model_device_paged_payload = None
    if real_model_device_resident_paged_decode is not None:
        real_model_device_paged_payload = json.loads(real_model_device_resident_paged_decode.read_text(encoding="utf-8"))
        real_model_device_paged_payload["source"] = str(real_model_device_resident_paged_decode)
        real_model_device_paged_payload["source_sha256"] = sha256(real_model_device_resident_paged_decode)
        artifacts.append(write_json(output, "real_model_device_resident_paged_decode.json", real_model_device_paged_payload))

    real_model_device_microbatch_payload = None
    if real_model_device_resident_microbatch is not None:
        real_model_device_microbatch_payload = json.loads(real_model_device_resident_microbatch.read_text(encoding="utf-8"))
        real_model_device_microbatch_payload["source"] = str(real_model_device_resident_microbatch)
        real_model_device_microbatch_payload["source_sha256"] = sha256(real_model_device_resident_microbatch)
        artifacts.append(write_json(output, "real_model_device_resident_microbatch.json", real_model_device_microbatch_payload))

    real_model_device_arrival_payload = None
    if real_model_device_resident_arrival_load is not None:
        real_model_device_arrival_payload = json.loads(real_model_device_resident_arrival_load.read_text(encoding="utf-8"))
        real_model_device_arrival_payload["source"] = str(real_model_device_resident_arrival_load)
        real_model_device_arrival_payload["source_sha256"] = sha256(real_model_device_resident_arrival_load)
        artifacts.append(write_json(output, "real_model_device_resident_arrival_load.json", real_model_device_arrival_payload))

    real_model_device_stress_payload = None
    if real_model_device_resident_arrival_stress is not None:
        real_model_device_stress_payload = json.loads(real_model_device_resident_arrival_stress.read_text(encoding="utf-8"))
        real_model_device_stress_payload["source"] = str(real_model_device_resident_arrival_stress)
        real_model_device_stress_payload["source_sha256"] = sha256(real_model_device_resident_arrival_stress)
        artifacts.append(write_json(output, "real_model_device_resident_arrival_stress.json", real_model_device_stress_payload))

    real_model_sdpa_payload = None
    if real_model_sdpa_backend is not None:
        real_model_sdpa_payload = json.loads(real_model_sdpa_backend.read_text(encoding="utf-8"))
        real_model_sdpa_payload["source"] = str(real_model_sdpa_backend)
        real_model_sdpa_payload["source_sha256"] = sha256(real_model_sdpa_backend)
        artifacts.append(write_json(output, "real_model_sdpa_backend.json", real_model_sdpa_payload))

    if real_model_device_arrival_payload is not None:
        artifacts.append(write_json(
            output,
            "real_model_end_to_end_serving_verdict.json",
            build_end_to_end_serving_verdict(real_model_device_arrival_payload, real_model_device_stress_payload),
        ))

    mlp_package = build_contract(MLP_MODEL, "robotics", "sim-wearable-v0", "prefill", physical_gate, True)
    artifacts.extend(add_contract_files(output, "mlp_prefill", mlp_package))
    attention_package = build_contract(ATTENTION_MODEL, "robotics", "sim-wearable-v0", "decode", physical_gate, False)
    artifacts.extend(add_contract_files(output, "attention_decode", attention_package))

    mlp_comparison = run_comparison(MLP_MODEL, "robotics", "sim-wearable-v0", "prefill", 0.001, 7, None, False)
    artifacts.append(write_json(output, "mlp_hybrid_output_comparison.json", mlp_comparison))
    attention_decode = run_decode(ATTENTION_MODEL, 6, 0.001, 7, "robotics", "sim-wearable-v0", None, False)
    artifacts.append(write_json(output, "attention_decode_comparison.json", attention_decode))

    calibrated = None
    calibration_import = None
    if CALIBRATED_PROFILE.exists():
        calibration_import = import_profile(ATTENTION_MODEL, CALIBRATED_PROFILE)
        artifacts.append(write_json(output, "attention_calibration_import.json", calibration_import))
        if calibration_import["acceptance"]["passed"]:
            calibrated = run_decode(
                ATTENTION_MODEL,
                6,
                0.0,
                7,
                "robotics",
                "crosssim-held-out-affine-attention-block-v0",
                None,
                False,
                CALIBRATED_PROFILE,
            )
            artifacts.append(write_json(output, "attention_decode_calibrated.json", calibrated))

    tiny_decode = run_tiny_decode(TINY_MODEL, [1, 2], 4, 0.001, 7, "robotics", "sim-wearable-v0", None, False)
    artifacts.append(write_json(output, "tiny_causal_lm_decode.json", tiny_decode))
    if include_reliability:
        reliability = run_sweep(TINY_MODEL, [1, 2], 4, [0.0, 0.001, 0.003, 0.005, 0.01], [7, 11, 19, 23], "robotics", "sim-wearable-v0")
        artifacts.append(write_json(output, "tiny_causal_lm_reliability.json", reliability))
    benchmark = run_benchmark(TINY_MODEL, [1, 2], 4, 0.001, 7, 20, 3, 3.0, 0.6, 2.0, 0.2, physical_gate, True)
    artifacts.append(write_json(output, "tiny_causal_lm_cost_benchmark.json", benchmark))
    if real_model_characterization_payload is not None:
        bridge = build_hybrid_cost_bridge(real_model_characterization_payload, benchmark, physical_gate or {}, real_model_extended_payload)
        artifacts.append(write_json(output, "real_model_hybrid_cost_bridge.json", bridge))
    if real_model_characterization_payload is not None and real_model_extended_payload is not None:
        workload_contract = build_workload_hardware_contract(
            real_model_characterization_payload,
            real_model_extended_payload,
            physical_gate or {},
            build_end_to_end_serving_verdict(real_model_device_arrival_payload, real_model_device_stress_payload)
            if real_model_device_arrival_payload else None,
        )
        artifacts.append(write_json(output, "real_model_workload_hardware_contract.json", workload_contract))
        if real_model_device_arrival_payload is not None:
            artifacts.append(write_json(
                output,
                "real_model_architecture_decision.json",
                build_real_model_architecture_decision(
                    build_end_to_end_serving_verdict(real_model_device_arrival_payload, real_model_device_stress_payload),
                    workload_contract,
                    physical_gate or {},
                    real_model_sdpa_payload,
                ),
            ))

    claim_report = {
        "schema_version": "transformer-vertical-slice-claim-report-v0.1",
        "allowed_claims": [
            "The named ONNX fixtures have reproducible operator placement and movement contracts.",
            "The tiny causal fixture has an explicit token-level decode, KV-cache accounting, reliability sweep, and cost denominator.",
            "The matching attention fixture can import and replay the declared calibrated CrossSim residual profile.",
            "The imported Google Colab Tesla T4 run measured real GPT-2 output parity, synchronized prefill/decode timing, KV allocator peaks, and bounded batch behavior for its recorded protocol.",
            "For that recorded GPT-2/T4 scope, cached generation was not proven uniformly faster than uncached generation.",
            "For the accepted bounded arrival trace, device-resident paged decode preserved exact GPT-2 output parity and delivered measured batching speedup over independent singles.",
            "The current end-to-end T4 verdict identifies device-resident kernel/allocator overhead as the next digital optimization target.",
        ],
        "refused_claims": [
            "Full production LLM support.",
            "Measured accelerator or silicon latency and energy.",
            "A general runtime win or isolated energy-per-token claim from the bounded arrival-trace power samples.",
            "Physical converter signoff, broad PVT coverage, or production readiness.",
            "Applying the attention calibration profile to a different model.",
        ],
        "evidence_status": {
            "mlp_contract": "passed",
            "attention_decode": "passed",
            "tiny_token_decode": "passed" if tiny_decode["acceptance"]["passed"] else "failed",
            "reliability": "recorded_distribution; not physical reliability",
            "calibrated_attention_profile": "passed" if calibration_import and calibration_import["acceptance"]["passed"] else "not_imported_or_failed",
            "cost_benchmark": "modeled energy plus reference timing; not hardware measurement",
            "physical_gate": physical_gate_audit["status"] if physical_gate_audit else "not_imported",
            "physical_gate_missing_artifacts": physical_gate_audit["extracted_artifacts"]["missing_paths"] if physical_gate_audit else [],
            "physical_candidate_readiness": physical_gate_audit.get("candidate_readiness") if physical_gate_audit else {"status": "not_imported"},
            "active_macro_candidate": physical_gate_audit.get("active_macro_candidate") if physical_gate_audit else {"status": "not_imported"},
            "active_macro_transient": physical_gate_audit.get("active_macro_transient") if physical_gate_audit else {"status": "not_imported"},
            "coupled_dac_comparator_bit": physical_gate_audit.get("coupled_dac_comparator_bit") if physical_gate_audit else {"status": "not_imported"},
            "real_model_inference": real_model_import or {"status": "not_imported"},
            "real_model_intake": {
                "status": "imported" if real_model_intake_payload else "not_imported",
                "evidence_kind": real_model_intake_payload.get("evidence_kind") if real_model_intake_payload else None,
                "model": real_model_intake_payload.get("model_profile") if real_model_intake_payload else None,
            },
            "real_model_serving_comparison": {
                "status": "imported" if real_model_serving_payload else "not_imported",
                "evidence_kind": real_model_serving_payload.get("evidence_kind") if real_model_serving_payload else None,
                "gpu_execution_accepted": real_model_serving_payload.get("gpu_execution_accepted") if real_model_serving_payload else False,
                "output_parity": all(row.get("output_parity", False) for row in real_model_serving_payload.get("rows", [])) if real_model_serving_payload else None,
            },
            "real_model_decision": {
                "status": "imported" if real_model_serving_payload else "not_imported",
                "decision": build_decision(real_model_serving_payload, real_model_characterization_payload, real_model_extended_payload)["decision"] if real_model_serving_payload else None,
                "measured_bottleneck": build_decision(real_model_serving_payload, real_model_characterization_payload, real_model_extended_payload).get("measured_bottleneck") if real_model_serving_payload else None,
                "extended_measurements": build_decision(real_model_serving_payload, real_model_characterization_payload, real_model_extended_payload).get("extended_measurements") if real_model_serving_payload else None,
            },
            "real_model_serving_characterization": {
                "status": "imported" if real_model_characterization_payload else "not_imported",
                "evidence_kind": real_model_characterization_payload.get("evidence_kind") if real_model_characterization_payload else None,
                "device_name": real_model_characterization_payload.get("device_name") if real_model_characterization_payload else None,
                "batch_sizes": real_model_characterization_payload.get("protocol", {}).get("batch_sizes", []) if real_model_characterization_payload else [],
                "output_parity": all(row.get("output_parity", False) for row in real_model_characterization_payload.get("rows", [])) if real_model_characterization_payload else None,
            },
            "real_model_serving_extended_characterization": {
                "status": "imported" if real_model_extended_payload else "not_imported",
                "evidence_kind": real_model_extended_payload.get("evidence_kind") if real_model_extended_payload else None,
                "context_rows": len(real_model_extended_payload.get("context_sweep", [])) if real_model_extended_payload else 0,
                "tail_latency_status": "measured" if real_model_extended_payload and real_model_extended_payload.get("tail_latency") else "not_imported",
                "operator_profile_status": real_model_extended_payload.get("operator_data_movement_profile", {}).get("status") if real_model_extended_payload else None,
                "power_status": real_model_extended_payload.get("protocol", {}).get("power", {}).get("status") if real_model_extended_payload else None,
            },
            "real_model_hybrid_cost_bridge": {
                "status": "imported" if real_model_characterization_payload else "not_imported",
                "decision": "digital_execution_with_analog_candidate_blocked" if real_model_characterization_payload else None,
                "analog_allowed_for_physical_claim": bool((physical_gate or {}).get("analog_allowed_for_physical_claim", False)) if real_model_characterization_payload else False,
                "extended_measurements_attached": bool(real_model_extended_payload),
            },
            "real_model_workload_hardware_contract": {
                "status": "derived_from_measured_gpu" if real_model_characterization_payload and real_model_extended_payload else "not_imported",
                "decision": "pursue_decode_first_digital_runtime_optimization_before_analog_placement" if real_model_characterization_payload and real_model_extended_payload else None,
            },
            "real_model_candidate_comparison": {
                "status": "imported" if real_model_candidate_payload else "not_imported",
                "decision": real_model_candidate_payload.get("decision") if real_model_candidate_payload else None,
                "output_parity": all(row.get("output_parity", False) for row in real_model_candidate_payload.get("rows", [])) if real_model_candidate_payload else None,
            },
            "real_model_microbatch_candidate": {
                "status": "imported" if real_model_microbatch_payload else "not_imported",
                "decision": real_model_microbatch_payload.get("decision") if real_model_microbatch_payload else None,
                "output_parity": real_model_microbatch_payload.get("result", {}).get("output_parity") if real_model_microbatch_payload else None,
                "throughput_speedup": real_model_microbatch_payload.get("result", {}).get("throughput_speedup") if real_model_microbatch_payload else None,
            },
            "real_model_continuous_microbatch": {
                "status": "imported" if real_model_continuous_payload else "not_imported",
                "decision": real_model_continuous_payload.get("decision") if real_model_continuous_payload else None,
                "output_parity": real_model_continuous_payload.get("result", {}).get("output_parity") if real_model_continuous_payload else None,
                "throughput_speedup": real_model_continuous_payload.get("result", {}).get("throughput_speedup") if real_model_continuous_payload else None,
                "groups": real_model_continuous_payload.get("result", {}).get("groups") if real_model_continuous_payload else None,
            },
            "real_model_paged_cache_adapter": {
                "status": "imported" if real_model_paged_payload else "not_imported",
                "decision": real_model_paged_payload.get("decision") if real_model_paged_payload else None,
                "output_parity": all(row.get("output_parity", False) for row in real_model_paged_payload.get("rows", [])) if real_model_paged_payload else None,
                "overhead_ratios": [row.get("paged_adapter_overhead_ratio") for row in real_model_paged_payload.get("rows", [])] if real_model_paged_payload else [],
            },
            "real_model_paged_attention_kernel": {
                "status": "imported" if real_model_paged_kernel_payload else "not_imported",
                "decision": real_model_paged_kernel_payload.get("decision") if real_model_paged_kernel_payload else None,
                "device": real_model_paged_kernel_payload.get("device_name") if real_model_paged_kernel_payload else None,
                "parity": all(row.get("parity", False) for row in real_model_paged_kernel_payload.get("rows", [])) if real_model_paged_kernel_payload else None,
                "kernel_ms_median": [row.get("kernel_ms_median") for row in real_model_paged_kernel_payload.get("rows", [])] if real_model_paged_kernel_payload else [],
            },
            "real_model_fused_paged_decode": {
                "status": "imported" if real_model_fused_paged_payload else "not_imported",
                "decision": real_model_fused_paged_payload.get("decision") if real_model_fused_paged_payload else None,
                "device": real_model_fused_paged_payload.get("device_name") if real_model_fused_paged_payload else None,
                "patched_attention_layers": real_model_fused_paged_payload.get("protocol", {}).get("patched_attention_layers") if real_model_fused_paged_payload else None,
                "output_parity": all(row.get("output_parity", False) for row in real_model_fused_paged_payload.get("rows", [])) if real_model_fused_paged_payload else None,
                "overhead_ratios": [row.get("fused_overhead_ratio") for row in real_model_fused_paged_payload.get("rows", [])] if real_model_fused_paged_payload else [],
            },
            "real_model_device_resident_paged_decode": {
                "status": "imported" if real_model_device_paged_payload else "not_imported",
                "decision": real_model_device_paged_payload.get("decision") if real_model_device_paged_payload else None,
                "device": real_model_device_paged_payload.get("device_name") if real_model_device_paged_payload else None,
                "patched_attention_layers": real_model_device_paged_payload.get("protocol", {}).get("patched_attention_layers") if real_model_device_paged_payload else None,
                "output_parity": all(row.get("output_parity", False) for row in real_model_device_paged_payload.get("rows", [])) if real_model_device_paged_payload else None,
                "overhead_ratios": [row.get("fused_overhead_ratio") for row in real_model_device_paged_payload.get("rows", [])] if real_model_device_paged_payload else [],
            },
            "real_model_device_resident_microbatch": {
                "status": "imported" if real_model_device_microbatch_payload else "not_imported",
                "decision": real_model_device_microbatch_payload.get("decision") if real_model_device_microbatch_payload else None,
                "device": real_model_device_microbatch_payload.get("device_name") if real_model_device_microbatch_payload else None,
                "batch_sizes": real_model_device_microbatch_payload.get("protocol", {}).get("batch_sizes") if real_model_device_microbatch_payload else [],
                "output_parity": all(row.get("output_parity", False) for row in real_model_device_microbatch_payload.get("rows", [])) if real_model_device_microbatch_payload else None,
                "overhead_ratios": [row.get("fused_overhead_ratio") for row in real_model_device_microbatch_payload.get("rows", [])] if real_model_device_microbatch_payload else [],
            },
            "real_model_device_resident_arrival_load": {
                "status": "imported" if real_model_device_arrival_payload else "not_imported",
                "decision": real_model_device_arrival_payload.get("decision") if real_model_device_arrival_payload else None,
                "device": real_model_device_arrival_payload.get("device_name") if real_model_device_arrival_payload else None,
                "groups": real_model_device_arrival_payload.get("result", {}).get("groups") if real_model_device_arrival_payload else [],
                "cancelled_request_indices": real_model_device_arrival_payload.get("result", {}).get("cancelled_request_indices") if real_model_device_arrival_payload else [],
                "output_parity": real_model_device_arrival_payload.get("result", {}).get("output_parity") if real_model_device_arrival_payload else None,
                "throughput_speedup": real_model_device_arrival_payload.get("result", {}).get("throughput_speedup") if real_model_device_arrival_payload else None,
            },
            "real_model_device_resident_arrival_stress": {
                "status": "imported" if real_model_device_stress_payload else "not_imported",
                "decision": real_model_device_stress_payload.get("decision") if real_model_device_stress_payload else None,
                "device": real_model_device_stress_payload.get("device_name") if real_model_device_stress_payload else None,
                "output_parity": real_model_device_stress_payload.get("result", {}).get("output_parity") if real_model_device_stress_payload else None,
                "throughput_speedup": real_model_device_stress_payload.get("result", {}).get("throughput_speedup") if real_model_device_stress_payload else None,
                "peak_memory_mb": real_model_device_stress_payload.get("result", {}).get("device_resident_scheduled", {}).get("peak_memory_allocated_mb") if real_model_device_stress_payload else None,
            },
            "real_model_end_to_end_serving_verdict": {
                "status": "derived_from_measured_gpu" if real_model_device_arrival_payload else "not_imported",
                "decision": build_end_to_end_serving_verdict(real_model_device_arrival_payload, real_model_device_stress_payload).get("decision") if real_model_device_arrival_payload else None,
                "recommendation": build_end_to_end_serving_verdict(real_model_device_arrival_payload, real_model_device_stress_payload).get("recommendation") if real_model_device_arrival_payload else None,
            },
            "real_model_sdpa_backend": {
                "status": "imported" if real_model_sdpa_payload else "not_imported",
                "decision": real_model_sdpa_payload.get("decision") if real_model_sdpa_payload else None,
                "device": real_model_sdpa_payload.get("device_name") if real_model_sdpa_payload else None,
                "output_parity": real_model_sdpa_payload.get("result", {}).get("output_parity") if real_model_sdpa_payload else None,
                "latency_ratio": real_model_sdpa_payload.get("result", {}).get("sdpa_over_eager_latency_ratio") if real_model_sdpa_payload else None,
            },
        },
        "model_level_decision": {
            "cached_vs_uncached": build_decision(real_model_serving_payload, real_model_characterization_payload, real_model_extended_payload) if real_model_serving_payload else None,
            "optimized_candidate": {
                "decision": real_model_candidate_payload.get("decision") if real_model_candidate_payload else "not_measured",
                "scope": "recorded GPT-2/Tesla-T4 prompts and protocol" if real_model_candidate_payload else None,
                "recommendation": "promote_explicit_kv_decode_candidate_for_further_long-context_and-load_testing" if real_model_candidate_payload and real_model_candidate_payload.get("decision") == "candidate_accepted_for_recorded_scope" else "do_not_promote_candidate",
            },
            "microbatch_candidate": {
                "decision": real_model_microbatch_payload.get("decision") if real_model_microbatch_payload else "not_measured",
                "recommendation": "promote_padded_microbatch_for_further_arrival_and_paged_kv_testing" if real_model_microbatch_payload and real_model_microbatch_payload.get("decision") == "candidate_accepted_for_recorded_scope" else "do_not_promote_candidate",
            },
            "continuous_microbatch_candidate": {
                "decision": real_model_continuous_payload.get("decision") if real_model_continuous_payload else "not_measured",
                "recommendation": "promote_bounded_arrival_window_for_paged_kv_and_cancellation_testing" if real_model_continuous_payload and real_model_continuous_payload.get("decision") == "candidate_accepted_for_recorded_scope" else "do_not_promote_candidate",
            },
            "paged_cache_adapter": {
                "decision": real_model_paged_payload.get("decision") if real_model_paged_payload else "not_measured",
                "recommendation": "retain_functional_adapter_and_replace_python_gather_repack_with_fused_paged_attention" if real_model_paged_payload and real_model_paged_payload.get("decision") == "paged_cache_functionally_accepted_overhead_requires_fused_kernel" else "repair_cache_adapter_before_promotion",
            },
            "paged_attention_kernel": {
                "decision": real_model_paged_kernel_payload.get("decision") if real_model_paged_kernel_payload else "not_measured",
                "recommendation": "promote_cuda_paged_attention_as_the_kernel_boundary_for_further_full_model_fusion" if real_model_paged_kernel_payload and real_model_paged_kernel_payload.get("decision") == "real_model_paged_kernel_parity_passed" else "repair_cuda_paged_attention_before_promotion",
            },
            "fused_paged_decode": {
                "decision": real_model_fused_paged_payload.get("decision") if real_model_fused_paged_payload else "not_measured",
                "recommendation": "replace_python_page_allocation_with_device_resident_allocator_and_remeasure" if real_model_fused_paged_payload and real_model_fused_paged_payload.get("decision") == "end_to_end_fused_paged_decode_parity_passed" else "complete_end_to_end_fused_decode_parity_first",
            },
            "device_resident_paged_decode": {
                "decision": real_model_device_paged_payload.get("decision") if real_model_device_paged_payload else "not_measured",
                "recommendation": "extend_to_long_context_load_and_power_matrix" if real_model_device_paged_payload and real_model_device_paged_payload.get("decision") == "end_to_end_fused_paged_decode_parity_passed" else "complete_device_resident_decode_parity_first",
            },
            "device_resident_microbatch": {
                "decision": real_model_device_microbatch_payload.get("decision") if real_model_device_microbatch_payload else "not_measured",
                "recommendation": "extend_device_resident_path_to_arrival_trace_and_memory_pressure" if real_model_device_microbatch_payload and real_model_device_microbatch_payload.get("decision") == "end_to_end_fused_paged_decode_parity_passed" else "complete_device_resident_microbatch_parity_first",
            },
            "device_resident_arrival_load": {
                "decision": real_model_device_arrival_payload.get("decision") if real_model_device_arrival_payload else "not_measured",
                "recommendation": "run_memory_pressure_and_longer_arrival_matrix" if real_model_device_arrival_payload and real_model_device_arrival_payload.get("decision") == "device_resident_arrival_load_parity_passed" else "repair_arrival_load_parity_first",
            },
            "device_resident_arrival_stress": {
                "decision": real_model_device_stress_payload.get("decision") if real_model_device_stress_payload else "not_measured",
                "recommendation": "optimize_native_scheduled_comparison_before_runtime_promotion" if real_model_device_stress_payload and real_model_device_stress_payload.get("decision") == "device_resident_arrival_load_parity_passed" else "repair_stress_parity_first",
            },
            "claim_boundary": "The candidate result is a bounded Colab serving decision; it is not a silicon or analog benefit claim.",
        },
        "next_gate": "Retain native digital attention as the serving baseline. Reopen the custom paged/persistent candidate only with a materially better backend or kernel and the same exact-parity, repeated T4 acceptance protocol. Keep the Sky130 converter gate downstream; it is not device evidence and must not block the Colab model-level decision.",
    }
    artifacts.append(write_json(output, "claim_report.json", claim_report))
    manifest = {
        "schema_version": "transformer-vertical-slice-manifest-v0.1",
        "artifacts": {},
        "source_models": {str(path.name): sha256(path) for path in [MLP_MODEL, ATTENTION_MODEL, TINY_MODEL]},
        "source_profiles": {
            str(path.name): sha256(path)
            for path in [PHYSICAL_GATE, CALIBRATED_PROFILE]
            if path.exists()
        },
    }
    if real_model_intake_payload:
        real_profile = real_model_intake_payload.get("model_profile", {})
        manifest["real_model_source"] = {
            "model_id": real_profile.get("model_id"),
            "model_revision": real_profile.get("model_revision"),
            "tokenizer_id": real_profile.get("tokenizer_id"),
            "tokenizer_revision": real_profile.get("tokenizer_revision"),
            "intake_artifact": "real_model_intake.json",
        }
    for name in sorted(set(artifacts)):
        manifest["artifacts"][name] = sha256(output / name)
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {"output": str(output), "artifact_count": len(manifest["artifacts"]), "manifest": str(manifest_path), "claim_report": claim_report}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-reliability", action="store_true")
    parser.add_argument("--real-model-evidence", type=Path)
    parser.add_argument("--real-model-intake", type=Path)
    parser.add_argument("--real-model-serving-comparison", type=Path)
    parser.add_argument("--real-model-serving-characterization", type=Path)
    parser.add_argument("--real-model-serving-extended-characterization", type=Path)
    parser.add_argument("--real-model-candidate-comparison", type=Path)
    parser.add_argument("--real-model-microbatch-candidate", type=Path)
    parser.add_argument("--real-model-continuous-microbatch", type=Path)
    parser.add_argument("--real-model-paged-cache-adapter", type=Path)
    parser.add_argument("--real-model-paged-attention-kernel", type=Path)
    parser.add_argument("--real-model-fused-paged-decode", type=Path)
    parser.add_argument("--real-model-device-resident-paged-decode", type=Path)
    parser.add_argument("--real-model-device-resident-microbatch", type=Path)
    parser.add_argument("--real-model-device-resident-arrival-load", type=Path)
    parser.add_argument("--real-model-device-resident-arrival-stress", type=Path)
    parser.add_argument("--real-model-sdpa-backend", type=Path)
    args = parser.parse_args()
    result = run_vertical_slice(
        args.output,
        include_reliability=not args.skip_reliability,
        real_model_evidence=args.real_model_evidence,
        real_model_intake=args.real_model_intake,
        real_model_serving_comparison=args.real_model_serving_comparison,
        real_model_serving_characterization=args.real_model_serving_characterization,
        real_model_serving_extended_characterization=args.real_model_serving_extended_characterization,
        real_model_candidate_comparison=args.real_model_candidate_comparison,
        real_model_microbatch_candidate=args.real_model_microbatch_candidate,
        real_model_continuous_microbatch=args.real_model_continuous_microbatch,
        real_model_paged_cache_adapter=args.real_model_paged_cache_adapter,
        real_model_paged_attention_kernel=args.real_model_paged_attention_kernel,
        real_model_fused_paged_decode=args.real_model_fused_paged_decode,
        real_model_device_resident_paged_decode=args.real_model_device_resident_paged_decode,
        real_model_device_resident_microbatch=args.real_model_device_resident_microbatch,
        real_model_device_resident_arrival_load=args.real_model_device_resident_arrival_load,
        real_model_device_resident_arrival_stress=args.real_model_device_resident_arrival_stress,
        real_model_sdpa_backend=args.real_model_sdpa_backend,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
