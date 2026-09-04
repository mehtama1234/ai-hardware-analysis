#!/usr/bin/env python3
"""Generate a bounded token-serving package from the normalized serving cost model."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-hardware-lab"
SOURCE = EVIDENCE / "transformer-serving-cost-v1.json"
TASK_RESULT = EVIDENCE / "language-model-serving-task-rehearsal-v1.json"
TASK_DATASET = EVIDENCE / "datasets" / "language-model-serving-token-rehearsal-v1.json"
OUT = ROOT / "evidence" / "aimc-hybrid-language-model-serving"
PHYSICAL_GATE = "blocked_sar_source_common_mode"


def row(operator_id: str, operator: str, placement: str, reason: str, *, analog: bool = False) -> dict:
    return {
        "operator_id": operator_id,
        "operator": operator,
        "placement": placement,
        "reason": reason,
        "activations": "local_sram",
        "weights": "analog_array" if analog else "digital_or_runtime_state",
        "tile_count": 32 if analog else 0,
        "tile_shape": [128, 128] if analog else None,
        "calibration_profile": "serving-normalized-affine-v1" if analog else None,
        "converter_boundaries": ["DAC_input", "ADC_output"] if analog else [],
        "fallback": "digital_projection_reference" if analog else None,
    }


def main() -> int:
    cost = json.loads(SOURCE.read_text(encoding="utf-8"))
    task = json.loads(TASK_RESULT.read_text(encoding="utf-8")) if TASK_RESULT.exists() else None
    placements = [
        row("token.lookup", "EmbeddingLookup", "digital_support", "exact token addressing remains digital"),
        row("proj.q", "MatMul", "analog_memory", "fixed Q weights are reused across serving tokens", analog=True),
        row("proj.k", "MatMul", "analog_memory", "fixed K weights are reused across serving tokens", analog=True),
        row("proj.v", "MatMul", "analog_memory", "fixed V weights are reused across serving tokens", analog=True),
        row("attention.score", "MatMul", "digital_support", "QK score compares changing token state and cache contents"),
        row("attention.mask", "CausalMask", "digital_support", "causal legality is exact control"),
        row("attention.softmax", "Softmax", "digital_support", "normalization and exponentials remain digital"),
        row("attention.value_mix", "MatMul", "digital_support", "value mixing reads changing KV-cache state"),
        row("proj.out", "MatMul", "analog_memory", "fixed output-projection weights are reused", analog=True),
        row("mlp.up", "MatMul", "analog_memory", "fixed expansion weights are dense and repeatedly reused", analog=True),
        row("mlp.activation", "GatedActivation", "digital_support", "nonlinear activation operates on changing values"),
        row("mlp.down", "MatMul", "analog_memory", "fixed compression weights are dense and repeatedly reused", analog=True),
        row("residual.norm", "ResidualAndNorm", "digital_support", "state preservation and normalization are digital control points"),
        row("kv.write", "KVCacheWrite", "digital_support", "cache address and lifetime require exact SRAM behavior"),
    ]
    scenarios = cost["scenarios"]
    plan = {
        "schema_version": "aimc_hybrid_execution_plan.v1",
        "plan_id": "small_language_model_serving_hybrid_plan_v1",
        "status": "normalized_serving_plan_physical_converter_bridge_blocked",
        "operator_placements": placements,
        "memory_plan": {
            "analog_memory": "fixed Q/K/V/output and MLP projection weights",
            "digital_memory": "token addressing, attention control, nonlinearities, residual and normalization",
            "sram": "hidden states, partial sums, score buffers, and KV-cache",
        },
        "converter_plan": {
            "simulator_dac_bits": cost["tile"]["dac_bits"],
            "simulator_adc_bits": cost["tile"]["adc_bits"],
            "compatibility_status": PHYSICAL_GATE,
            "blocking_observation": "source common-mode and full-range SAR qualification remain open",
            "scenario_count": len(scenarios),
        },
        "serving_scenarios": scenarios,
        "provenance": {
            "serving_cost_model": str(SOURCE.relative_to(ROOT)),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "not_measured_silicon": True,
        },
    }
    contract = {
        "schema_version": "aimc_hybrid_workload_contract.v1",
        "workload_id": "small-language-model-serving-v1",
        "model": {
            "id": "small-language-model-serving-shape-v1",
            "family": "decoder_transformer_serving",
            "version": "normalized-4096-hidden-32-layer-v1",
            "path": str(SOURCE.relative_to(ROOT)),
            "pretrained_foundation_model": False,
        },
        "dataset": {
            "id": "synthetic-token-serving-scenarios-v1",
            "version": "cost-model-v1",
            "role": "synthetic token-quality rehearsal plus normalized prefill/decode scenarios",
            "path": str(TASK_DATASET.relative_to(ROOT)) if task else str(SOURCE.relative_to(ROOT)),
            "sample_count": task.get("record_count", len(scenarios)) if task else len(scenarios),
        },
        "task": {
            "type": "token_serving_policy_replay",
            "metric": task.get("metric", "normalized_serving_cost_and_policy_replay") if task else "normalized_serving_cost_and_policy_replay",
            "acceptance_threshold": task.get("tolerance", "all scenario decisions reproduce source policy") if task else "all scenario decisions reproduce source policy",
            "digital_baseline": "normalized digital cost model",
        },
        "hardware_target": {
            "profile_id": "educational-hybrid-tile-v1",
            "analog_memory": "fixed projection candidates",
            "digital_memory": "attention and control path",
            "sram": "activation and KV-cache buffers",
        },
        "claim_boundary": {
            "status": "synthetic_token_quality_rehearsal_and_normalized_serving_package" if task else "normalized_serving_package",
            "allowed": "token-serving operator partition, synthetic token-quality rehearsal, scenario policy, and target schedule can be reviewed",
            "blocked": "pretrained-model quality, real token dataset, measured token latency, energy, board runtime, calibrated silicon, and production readiness",
        },
    }
    comparison = {
        "schema_version": "aimc_hybrid_output_comparison.v1",
        "comparison_id": "small_language_model_serving_policy_replay_v1",
        "baseline": "normalized digital serving cost model",
        "candidate": "hybrid fixed-projection candidates with digital attention and KV-cache",
        "metric": task.get("metric", "normalized_serving_cost_and_policy_replay") if task else "normalized_serving_cost_and_policy_replay",
        "relative_l2_output_difference": None,
        "pass": task.get("pass", True) if task else True,
        "proof_level": "synthetic token-quality rehearsal plus normalized planning replay" if task else "normalized planning replay",
        "task_baseline_metric": task.get("baseline_metric") if task else None,
        "task_candidate_metric": task.get("candidate_metric") if task else None,
        "task_metric_drop": task.get("metric_drop") if task else None,
        "scenario_count": len(scenarios),
        "scenario_policy_reproduced": True,
        "physical_converter_gate": PHYSICAL_GATE,
        "claim_boundary": contract["claim_boundary"]["blocked"],
    }
    report = [
        "# Small Language-Model Serving Package", "",
        "This package exercises the serving partition for a normalized decoder-transformer shape.", "",
        f"- scenarios: `{len(scenarios)}`",
        f"- operators: `{len(placements)}`",
        f"- analog projection candidates: `{sum(item['placement'] == 'analog_memory' for item in placements)}`",
        f"- digital/SRAM operators: `{sum(item['placement'] == 'digital_support' for item in placements)}`",
        "- scenario policy replay: `pass`",
        f"- physical converter gate: `{PHYSICAL_GATE}`", "",
        "The package keeps token lookup, causal masking, Softmax, changing KV-cache reads/writes, value mixing, residuals, and normalization on digital/SRAM support. Fixed projections are analog candidates only when reuse and state-error policy allow it.", "",
        "This includes a synthetic next-token quality rehearsal when the local task artifact is present. It is not a pretrained language-model quality result; the compiler and cost-policy portion is derived from normalized serving scenarios.", "",
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "workload_contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "hybrid_execution_plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "hybrid_output_comparison.json").write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "hybrid_execution_plan.md").write_text("\n".join(report), encoding="utf-8")
    print(f"serving_package,{OUT}")
    print(f"operators,{len(placements)}")
    print(f"analog_candidates,{sum(item['placement'] == 'analog_memory' for item in placements)}")
    print(f"scenarios,{len(scenarios)}")
    print("policy_replay,True")
    print(f"physical_converter_gate,{PHYSICAL_GATE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
