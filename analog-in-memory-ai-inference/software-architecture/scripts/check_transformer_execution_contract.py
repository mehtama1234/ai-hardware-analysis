#!/usr/bin/env python3
"""Smoke-check the first transformer execution-contract builder."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from build_transformer_execution_contract import build_contract
from run_transformer_output_comparison import run_comparison
from run_transformer_decode_comparison import run_decode
from run_tiny_causal_lm_decode import run as run_tiny_causal_lm
from run_tiny_causal_lm_reliability_sweep import run_sweep
from import_attention_calibration_profile import import_profile
from import_physical_converter_gate import import_gate
from benchmark_tiny_causal_lm import run_benchmark


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "samples" / "deep-transformer-mlp-stack.onnx"
ATTENTION_MODEL = ROOT / "samples" / "attention-block.onnx"
TINY_CAUSAL_MODEL = ROOT / "samples" / "tiny-causal-lm.onnx"
CALIBRATED_ATTENTION_PROFILE = ROOT.parent.parent / "analog-digital-chip-design-eda" / "evidence" / "aimc-simulator-adapters" / "crosssim-calibrated-attention-block-analog-error-simulation.json"
PHYSICAL_GATE = ROOT.parent.parent / "analog-digital-chip-design-eda" / "evidence" / "aimc-simulator-adapters" / "analog-converter-physical-cell-gate.json"
PHYSICAL_GATE = ROOT.parent.parent / "analog-digital-chip-design-eda" / "evidence" / "aimc-simulator-adapters" / "analog-converter-physical-cell-gate.json"


def main() -> None:
    package = build_contract(MODEL, "robotics", "sim-wearable-v0", "prefill")
    inventory = package["operator_inventory"]["operators"]
    movement = package["movement_ledger"]["rows"]
    schedule = package["hybrid_execution_plan"]["schedule"]
    assert len(inventory) == 36, len(inventory)
    assert sum(item["operator"] == "MatMul" for item in inventory) == 12
    assert len(movement) == len(inventory)
    assert len(schedule) == len(inventory)
    assert package["workload_contract"]["fallback_policy"] == "digital_fallback_on_physical_or_quality_gate_failure"
    assert "measured board latency" in package["claim_boundary"]["refused"]
    with tempfile.TemporaryDirectory(prefix="transformer-contract-check-") as directory:
        output = Path(directory)
        for name, payload in package.items():
            (output / f"{name}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert all(json.loads(path.read_text()) for path in output.glob("*.json"))
    attention = build_contract(ATTENTION_MODEL, "robotics", "sim-wearable-v0", "decode")
    attention_rows = {item["operator_id"]: item for item in attention["operator_inventory"]["operators"]}
    assert attention_rows["attn.scores.matmul"]["placement"] == "digital"
    assert attention_rows["attn.value.matmul"]["placement"] == "digital"
    assert {item["operator_id"] for item in attention["operator_inventory"]["state_operations"]} == {
        "kv_cache.read",
        "kv_cache.write",
    }
    assert attention["workload_contract"]["kv_cache"]["initial_policy"] == "digital_memory"
    if PHYSICAL_GATE.exists():
        physical_gate = json.loads(PHYSICAL_GATE.read_text(encoding="utf-8"))
        physical_gate["analog_allowed_for_physical_claim"] = bool(physical_gate.get("ready_for_candidate_post_layout_payload", False))
        constrained = build_contract(MODEL, "robotics", "sim-wearable-v0", "prefill", physical_gate, True)
        constrained_rows = constrained["operator_inventory"]["operators"]
        assert all(item["placement"] == "digital_fallback" for item in constrained_rows if item["fixed_weight_candidate"])
        assert constrained["workload_contract"]["physical_gate"]["status"] == "physical_cells_present_waiting_for_extracted_artifacts"
        comparison = run_comparison(MODEL, "robotics", "sim-wearable-v0", "prefill", 0.001, 7, physical_gate, True)
        assert comparison["contract"]["analog_candidate_count"] == 0
        assert comparison["weight_replay"]["applied"] == []
        assert comparison["metrics"]["relative_l2_error"] == 0.0
    comparison = run_comparison(MODEL, "robotics", "sim-wearable-v0", "prefill", 0.001, 7, None, False)
    assert comparison["contract"]["analog_candidate_count"] == 12
    assert len(comparison["weight_replay"]["applied"]) == 12
    assert comparison["acceptance"]["passed"]
    attention_comparison = run_comparison(ATTENTION_MODEL, "robotics", "sim-wearable-v0", "decode", 0.001, 7, None, False)
    assert attention_comparison["contract"]["analog_candidate_operator_ids"] == [
        "attn.q.matmul",
        "attn.k.matmul",
        "attn.v.matmul",
        "attn.out.matmul",
    ]
    assert attention_comparison["acceptance"]["passed"]
    decode = run_decode(ATTENTION_MODEL, 6, 0.001, 7, "robotics", "sim-wearable-v0", None, False)
    assert decode["contract"]["analog_candidate_count"] == 4
    assert decode["cache_and_movement"]["total_kv_cache_read_bytes"] == 960
    assert decode["cache_and_movement"]["total_kv_cache_write_bytes"] == 384
    assert decode["summary"]["output_channel_agreement_rate"] == 1.0
    assert decode["acceptance"]["passed"]
    tiny = run_tiny_causal_lm(TINY_CAUSAL_MODEL, [1, 2], 4, 0.001, 7, "robotics", "sim-wearable-v0", None, False)
    assert tiny["contract"]["analog_candidate_count"] == 5
    assert tiny["prefill_reference_parity"]["passed"]
    assert tiny["summary"]["free_running_exact_sequence_agreement"] == 1
    assert tiny["acceptance"]["passed"]
    sweep = run_sweep(TINY_CAUSAL_MODEL, [1, 2], 4, [0.0, 0.001], [7, 11], "robotics", "sim-wearable-v0")
    assert sweep["summary"]["case_count"] == 4
    assert sweep["summary"]["prefill_oracle_passed"]
    assert sweep["summary"]["acceptance_rate"] == 1.0
    if CALIBRATED_ATTENTION_PROFILE.exists():
        imported = import_profile(ATTENTION_MODEL, CALIBRATED_ATTENTION_PROFILE)
        assert imported["acceptance"]["passed"], imported["acceptance"]["errors"]
        assert imported["scope"]["candidate_count"] == 4
        calibrated_decode = run_decode(
            ATTENTION_MODEL,
            6,
            0.0,
            7,
            "robotics",
            "crosssim-held-out-affine-attention-block-v0",
            None,
            False,
            CALIBRATED_ATTENTION_PROFILE,
        )
        assert calibrated_decode["calibration_replay"]["import_acceptance"]["passed"]
        assert calibrated_decode["acceptance"]["passed"]
    if PHYSICAL_GATE.exists():
        gate_import = import_gate(PHYSICAL_GATE)
        assert gate_import["physical_cells"]["all_required_present"]
        assert gate_import["analog_allowed_for_physical_claim"] is False
        assert len(gate_import["extracted_artifacts"]["missing_paths"]) == 2
    benchmark = run_benchmark(TINY_CAUSAL_MODEL, [1, 2], 4, 0.001, 7, 2, 1, 3.0, 0.6, 2.0, 0.2, None, False)
    assert benchmark["summary"]["token_count"] == 6
    assert benchmark["summary"]["total_kv_cache_bytes"] == 1344
    assert benchmark["summary"]["modeled_energy_ratio_digital_over_hybrid"] > 1.0
    if PHYSICAL_GATE.exists():
        benchmark_gate = json.loads(PHYSICAL_GATE.read_text(encoding="utf-8"))
        benchmark_gate["analog_allowed_for_physical_claim"] = bool(benchmark_gate.get("ready_for_candidate_post_layout_payload", False))
        gated_benchmark = run_benchmark(TINY_CAUSAL_MODEL, [1, 2], 4, 0.001, 7, 2, 1, 3.0, 0.6, 2.0, 0.2, benchmark_gate, True)
        assert gated_benchmark["summary"]["modeled_energy_ratio_digital_over_hybrid"] == 1.0
    print("PASS transformer execution contract: placement, attention/KV policy, physical fallback, and output replay")


if __name__ == "__main__":
    main()
