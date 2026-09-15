#!/usr/bin/env python3
"""Verify the real-model decision package's minimum acceptance invariants."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    package = args.package
    intake = json.loads((package / "real_model_intake.json").read_text(encoding="utf-8"))
    serving = json.loads((package / "real_model_serving_comparison.json").read_text(encoding="utf-8"))
    decision = json.loads((package / "real_model_decision.json").read_text(encoding="utf-8"))
    characterization_path = package / "real_model_serving_characterization.json"
    extended_path = package / "real_model_serving_extended_characterization.json"
    contract_path = package / "real_model_workload_hardware_contract.json"
    candidate_path = package / "real_model_candidate_comparison.json"
    microbatch_path = package / "real_model_microbatch_candidate.json"
    continuous_path = package / "real_model_continuous_microbatch.json"
    paged_path = package / "real_model_paged_cache_adapter.json"
    paged_kernel_path = package / "real_model_paged_attention_kernel.json"
    fused_paged_path = package / "real_model_fused_paged_decode.json"
    device_paged_path = package / "real_model_device_resident_paged_decode.json"
    device_microbatch_path = package / "real_model_device_resident_microbatch.json"
    arrival_load_path = package / "real_model_device_resident_arrival_load.json"
    arrival_stress_path = package / "real_model_device_resident_arrival_stress.json"
    bridge_path = package / "real_model_hybrid_cost_bridge.json"
    verdict_path = package / "real_model_end_to_end_serving_verdict.json"
    architecture_path = package / "real_model_architecture_decision.json"
    sdpa_path = package / "real_model_sdpa_backend.json"
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    assert intake["model_profile"]["model_id"] == serving["model_profile"]["model_id"]
    assert intake["model_profile"]["tokenizer_id"] == serving["model_profile"]["tokenizer_id"]
    assert serving["rows"] and all(row["output_parity"] for row in serving["rows"])
    assert serving["evidence_kind"] in ("measured_cpu", "measured_gpu")
    assert decision["decision"] in ("hardware_measurement_pending", "cached_candidate_improves_measured_scope", "cached_candidate_not_proven_better")
    if characterization_path.exists():
        characterization = json.loads(characterization_path.read_text(encoding="utf-8"))
        assert characterization["evidence_kind"] == "measured_gpu"
        assert characterization["gpu_execution_accepted"] is True
        assert characterization["rows"] and all(row["output_parity"] for row in characterization["rows"])
        assert characterization["protocol"]["batch_sizes"] == [1, 2, 4]
    if extended_path.exists():
        extended = json.loads(extended_path.read_text(encoding="utf-8"))
        assert extended["evidence_kind"] == "measured_gpu"
        assert extended["gpu_execution_accepted"] is True
        assert len(extended["context_sweep"]) >= 4
        assert extended["tail_latency"]["latency"]["count"] >= 10
        assert len(extended["concurrency"]) >= 2
        assert extended["operator_data_movement_profile"]["status"] in ("measured_cuda_profiler", "unavailable")
        assert "power" in extended["protocol"]
    if contract_path.exists():
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        assert contract["evidence_kind"] == "derived_from_measured_gpu"
        assert contract["decision"] == "pursue_decode_first_digital_runtime_optimization_before_analog_placement"
        assert "KV_cache" in contract["placement_policy"]["digital_required"]
        denominators = contract.get("derived_digital_denominators")
        if denominators:
            assert denominators["transformer_layers"] == 12
            assert denominators["attention_heads"] == 12
            assert denominators["head_dimension"] == 64
            assert denominators["KV_bytes_per_token_all_layers_fp16"] == 36864
            assert denominators["single_query_attention_flops_per_history_token_all_layers"] == 36864
        if "serving_decision" in contract:
            assert contract["serving_decision"]["status"] == "measured_arrival_trace_attached"
            assert contract["serving_decision"]["candidate_decision"] == "device_resident_candidate_not_ready_for_runtime_promotion"
    if candidate_path.exists():
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        assert candidate["evidence_kind"] == "measured_gpu"
        assert candidate["gpu_execution_accepted"] is True
        assert candidate["rows"] and all(row["output_parity"] for row in candidate["rows"])
        assert candidate["decision"] in ("candidate_accepted_for_recorded_scope", "candidate_not_proven_better")
    if microbatch_path.exists():
        microbatch = json.loads(microbatch_path.read_text(encoding="utf-8"))
        assert microbatch["evidence_kind"] == "measured_gpu"
        assert microbatch["gpu_execution_accepted"] is True
        assert microbatch["result"]["output_parity"] is True
        assert microbatch["result"]["throughput_speedup"] > 1.0
    if continuous_path.exists():
        continuous = json.loads(continuous_path.read_text(encoding="utf-8"))
        assert continuous["evidence_kind"] == "measured_gpu"
        assert continuous["gpu_execution_accepted"] is True
        assert continuous["result"]["output_parity"] is True
        assert continuous["result"]["throughput_speedup"] > 1.0
        assert len(continuous["result"]["groups"]) >= 2
    if paged_path.exists():
        paged = json.loads(paged_path.read_text(encoding="utf-8"))
        assert paged["evidence_kind"] == "measured_gpu"
        assert paged["gpu_execution_accepted"] is True
        assert paged["rows"] and all(row["output_parity"] for row in paged["rows"])
    if paged_kernel_path.exists():
        paged_kernel = json.loads(paged_kernel_path.read_text(encoding="utf-8"))
        assert paged_kernel["evidence_kind"] == "measured_gpu"
        assert paged_kernel["gpu_execution_accepted"] is True
        assert paged_kernel["device_name"] == "Tesla T4"
        assert paged_kernel["rows"] and all(row["parity"] for row in paged_kernel["rows"])
    if fused_paged_path.exists():
        fused_paged = json.loads(fused_paged_path.read_text(encoding="utf-8"))
        assert fused_paged["evidence_kind"] == "measured_gpu"
        assert fused_paged["gpu_execution_accepted"] is True
        assert fused_paged["device_name"] == "Tesla T4"
        assert fused_paged["protocol"]["patched_attention_layers"] == 12
        assert fused_paged["rows"] and all(row["output_parity"] for row in fused_paged["rows"])
    if device_paged_path.exists():
        device_paged = json.loads(device_paged_path.read_text(encoding="utf-8"))
        assert device_paged["evidence_kind"] == "measured_gpu"
        assert device_paged["gpu_execution_accepted"] is True
        assert device_paged["device_name"] == "Tesla T4"
        assert device_paged["protocol"]["patched_attention_layers"] == 12
        assert "device-side" in device_paged["protocol"]["decode"]
        assert device_paged["rows"] and all(row["output_parity"] for row in device_paged["rows"])
    if device_microbatch_path.exists():
        device_microbatch = json.loads(device_microbatch_path.read_text(encoding="utf-8"))
        assert device_microbatch["evidence_kind"] == "measured_gpu"
        assert device_microbatch["gpu_execution_accepted"] is True
        assert device_microbatch["device_name"] == "Tesla T4"
        assert device_microbatch["protocol"]["batch_sizes"] == [1, 2, 4]
        assert device_microbatch["rows"] and all(row["output_parity"] for row in device_microbatch["rows"])
    if arrival_load_path.exists():
        arrival_load = json.loads(arrival_load_path.read_text(encoding="utf-8"))
        assert arrival_load["evidence_kind"] == "measured_gpu"
        assert arrival_load["gpu_execution_accepted"] is True
        assert arrival_load["device_name"] == "Tesla T4"
        assert arrival_load["result"]["output_parity"] is True
        if "persistent_output_parity" in arrival_load["result"]:
            assert arrival_load["result"]["persistent_output_parity"] is True
            assert arrival_load["result"]["device_persistent_scheduled"]["wall_time_ms_median"] > 0
        assert arrival_load["result"]["cancelled_request_indices"] == [7]
        assert len(arrival_load["result"]["groups"]) == 2
        assert arrival_load["result"]["device_resident_scheduled"]["power"]["status"] == "sampled_nvml_protocol_scope"
    if arrival_stress_path.exists():
        arrival_stress = json.loads(arrival_stress_path.read_text(encoding="utf-8"))
        assert arrival_stress["evidence_kind"] == "measured_gpu"
        assert arrival_stress["gpu_execution_accepted"] is True
        assert arrival_stress["device_name"] == "Tesla T4"
        assert arrival_stress["result"]["output_parity"] is True
        assert arrival_stress["result"]["device_resident_scheduled"]["peak_memory_allocated_mb"] > 900
        assert arrival_stress["result"]["device_resident_scheduled"]["power"]["status"] == "sampled_nvml_protocol_scope"
        assert paged["decision"] == "paged_cache_functionally_accepted_overhead_requires_fused_kernel"
    if bridge_path.exists():
        bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
        assert bridge["placement_decision"]["decision"] == "digital_execution_with_analog_candidate_blocked"
        assert bridge["placement_decision"]["analog_allowed_for_physical_claim"] is False
        assert bridge["measured_gpu_denominator"]["correctness"]["all_output_parity"] is True
    if verdict_path.exists():
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        assert verdict["evidence_kind"] == "measured_gpu"
        assert verdict["device"] == "Tesla T4"
        assert verdict["correctness"]["output_parity"] is True
        if verdict["measured_comparison"].get("direct_control_wall_time_ms_median") is not None:
            assert verdict["measured_comparison"]["direct_control_output_parity"] is True
            assert verdict["diagnostic_finding"] in (
                "page_packing_is_not_latency_dominant_in_this_trace",
                "page_packing_or_workspace_path_remains_a_candidate_overhead",
            )
        assert verdict["decision"] == "device_resident_candidate_not_ready_for_runtime_promotion"
        assert verdict["architecture_implication"]["analog_placement"] == "blocked_by_physical_converter_gate"
    if architecture_path.exists():
        architecture = json.loads(architecture_path.read_text(encoding="utf-8"))
        assert architecture["decision"] == "native_digital_serving_baseline_with_cuda_optimization_candidate"
        assert architecture["device_evidence"]["device"] == "Tesla T4"
        assert architecture["device_evidence"]["output_parity"] is True
        assert architecture["execution_placement"]["analog_regions"] == []
        assert architecture["evidence_gates"]["physical_converter_gate"] == "blocked"
    if sdpa_path.exists():
        sdpa = json.loads(sdpa_path.read_text(encoding="utf-8"))
        assert sdpa["evidence_kind"] == "measured_gpu"
        assert sdpa["device_name"] == "Tesla T4"
        assert sdpa["result"]["output_parity"] is True
        assert sdpa["decision"] == "native_sdpa_backend_not_proven_better"
    for name, expected_hash in manifest["artifacts"].items():
        assert (package / name).exists(), name
        assert sha256(package / name) == expected_hash, name
    print(json.dumps({"status": "passed", "model": serving["model_profile"]["model_id"], "rows": len(serving["rows"]), "evidence_kind": serving["evidence_kind"], "decision": decision["decision"], "manifest_artifacts": len(manifest["artifacts"])}, indent=2))


if __name__ == "__main__":
    main()
