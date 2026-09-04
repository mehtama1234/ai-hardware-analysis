#!/usr/bin/env python3
"""Generate a conservative hybrid plan for the attention-shaped fixture."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "evidence" / "aimc-simulator-adapters"
SUMMARY = SIM_DIR / "calibrated-attention-block-simulator-payload-run-summary.json"
CROSSSIM = SIM_DIR / "crosssim-calibrated-attention-block-analog-error-simulation.json"
OUT = ROOT / "evidence" / "aimc-hybrid-transformer-attention-slice"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    summary = read(SUMMARY)
    crosssim = read(CROSSSIM)
    candidates = summary["candidate_ids"]
    digital_ops = crosssim["error_model"]["array_assumptions"]["digital_only_attention_ops"]
    rows = []
    for candidate_id in candidates:
        rows.append(
            {
                "operator_id": candidate_id,
                "operator": "MatMul",
                "placement": "analog_memory",
                "weights": "analog_array",
                "activations": "local_sram",
                "tile_shape": [16, 16],
                "tile_count": 1,
                "converter_boundaries": ["DAC_input", "ADC_output"],
                "calibration_profile": "crosssim-held-out-affine-attention-block-v0",
                "fallback": "digital_projection_reference",
                "reason": "static projection weight reuse is an analog candidate; dynamic attention remains outside this row",
            }
        )
    reasons = {
        "attn.scores.matmul": "dynamic query-key score selection is sensitive to small errors",
        "attn.scale": "digital scaling keeps attention normalization explicit",
        "attn.softmax": "nonlinear probability normalization remains digital",
        "attn.value.matmul": "dynamic score-weighted value movement remains digital until cache and timing costs are measured",
    }
    for operator_id in digital_ops:
        rows.append(
            {
                "operator_id": operator_id,
                "operator": "attention_support",
                "placement": "digital_support",
                "weights": "digital_or_runtime_state",
                "activations": "local_sram",
                "tile_shape": None,
                "tile_count": 0,
                "converter_boundaries": [],
                "calibration_profile": None,
                "fallback": None,
                "reason": reasons[operator_id],
            }
        )

    impact = crosssim["accuracy_impact"]
    plan = {
        "schema_version": "aimc_hybrid_execution_plan.v1",
        "plan_id": "attention_block_hybrid_plan_v1",
        "status": "simulator_plan_physical_converter_bridge_blocked",
        "operator_placements": rows,
        "memory_plan": {
            "analog_memory": "static Q, K, V, and output projection weights",
            "digital_memory": "dynamic attention score, scaling, Softmax, and value selection",
            "sram": "token activations, Q/K/V buffers, score matrix, KV-cache placeholder, and fallback buffers",
        },
        "converter_plan": {
            "simulator_dac_bits": 8,
            "simulator_adc_bits": 8,
            "physical_diagnostic_bits": 4,
            "compatibility_status": "blocked_sar_source_common_mode",
            "blocking_observation": "physical PMOS-only converter code 14 to 15 spacing is 16.361 mV versus a 56.25 mV half-LSB target",
        },
        "provenance": {
            "source_model": summary["source_model"],
            "calibrated_summary": str(SUMMARY.relative_to(ROOT)),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "not_measured_silicon": True,
        },
    }
    contract = {
        "schema_version": "aimc_hybrid_workload_contract.v1",
        "workload_id": "attention_block_hybrid_vertical_slice_v1",
        "model": {"id": "attention-block", "version": "fixture-v1", "family": "attention-shaped transformer fixture", "pretrained_foundation_model": False, "path": summary["source_model"]},
        "dataset": {"id": "deterministic-attention-replay-v1", "version": "fixture-v1", "role": "held-out projection replay, not a task dataset", "sample_count": 3},
        "task": {"type": "attention-shaped numerical replay", "metric": impact["metric"], "acceptance_threshold": 0.15, "digital_baseline": "digital ONNX-weight attention block"},
        "hardware_target": {"analog_memory": "static projection weights", "digital_memory": "dynamic attention operations", "sram": "token and score buffers", "profile_id": "educational-hybrid-tile-v1"},
        "claim_boundary": {"status": "simulator_vertical_slice_only", "allowed": "calibrated simulator replay of static attention projections", "blocked": "full transformer token accuracy, KV-cache performance, calibrated silicon, board runtime, and production readiness"},
    }
    comparison = {
        "schema_version": "aimc_hybrid_output_comparison.v1",
        "comparison_id": "attention_block_crosssim_held_out_v1",
        "baseline": "digital ONNX-weight attention block",
        "candidate": "CrossSim calibrated static projections plus digital attention support",
        "metric": impact["metric"],
        "relative_l2_output_difference": impact["estimated_drop"],
        "threshold": 0.15,
        "pass": bool(impact["pass"]),
        "proof_level": "calibrated simulator replay",
        "physical_converter_gate": plan["converter_plan"]["compatibility_status"],
        "claim_boundary": "static projection replay only; dynamic attention operations remain digital and task accuracy is not proven",
        "source": str(CROSSSIM.relative_to(ROOT)),
    }
    report = "\n".join(
        [
            "# Hybrid Attention Vertical Slice",
            "",
            "This package separates static projection work from dynamic attention work.",
            "",
            "- analog candidates: `4` static projection MatMuls (`Q`, `K`, `V`, output)",
            "- digital support: `4` dynamic score, scale, Softmax, and value operations",
            "- SRAM: token activations, Q/K/V buffers, score matrix, KV-cache placeholder, and fallback buffers",
            f"- CrossSim replay: `{impact['estimated_drop']:.6g}` relative L2, pass `{str(impact['pass']).lower()}`",
            "- physical converter gate: `blocked_sar_source_common_mode`",
            "",
            "The simulator result does not prove that a full transformer can run on the chip. Dynamic attention and cache movement remain digital until their timing, memory, and task-impact evidence exists.",
            "",
        ]
    )
    OUT.mkdir(parents=True, exist_ok=True)
    for name, payload in {"workload_contract.json": contract, "hybrid_execution_plan.json": plan, "hybrid_output_comparison.json": comparison, "analog_error_replay.json": crosssim}.items():
        (OUT / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "hybrid_execution_plan.md").write_text(report, encoding="utf-8")
    print(f"attention_package,{OUT}")
    print(f"analog_projections,{len(candidates)}")
    print(f"digital_attention_ops,{len(digital_ops)}")
    print(f"simulator_relative_l2,{impact['estimated_drop']:.9g}")
    print(f"simulator_pass,{impact['pass']}")
    print(f"physical_converter_gate,{plan['converter_plan']['compatibility_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
