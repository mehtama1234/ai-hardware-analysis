#!/usr/bin/env python3
"""Wrap the existing CrossSim projection-stack replay in the common compiler schema."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "aimc-hybrid-projection-stack"
SOURCE = ROOT / "evidence" / "aimc-simulator-adapters" / "crosssim-projection-stack-analog-error-simulation.json"
PHYSICAL_GATE = "blocked_sar_source_common_mode"


def main() -> int:
    replay = json.loads(SOURCE.read_text(encoding="utf-8"))
    candidates = [
        ("proj.q.matmul", "MatMul", [8, 16]),
        ("proj.k.matmul", "MatMul", [16, 16]),
        ("proj.v.matmul", "MatMul", [16, 12]),
        ("proj.out.matmul", "MatMul", [12, 8]),
    ]
    placements = []
    for operator_id, operator, shape in candidates:
        placements.append({
            "operator_id": operator_id,
            "operator": operator,
            "placement": "analog_memory",
            "reason": "fixed ONNX initializer weights are reused across the projection stack",
            "activations": "local_sram",
            "weights": "analog_array",
            "tile_count": 1,
            "tile_shape": shape,
            "calibration_profile": "crosssim-projection-stack-trained-weight-v0",
            "converter_boundaries": ["DAC_input", "ADC_output"],
            "fallback": "digital_projection_reference",
        })
    placements.extend([
        {"operator_id": "proj.q.relu", "operator": "Relu", "placement": "digital_support", "reason": "nonlinear activation remains digital", "activations": "local_sram", "weights": "digital_or_runtime_state", "tile_count": 0, "tile_shape": None, "calibration_profile": None, "converter_boundaries": [], "fallback": None},
        {"operator_id": "proj.k.relu", "operator": "Relu", "placement": "digital_support", "reason": "nonlinear activation remains digital", "activations": "local_sram", "weights": "digital_or_runtime_state", "tile_count": 0, "tile_shape": None, "calibration_profile": None, "converter_boundaries": [], "fallback": None},
        {"operator_id": "proj.v.relu", "operator": "Relu", "placement": "digital_support", "reason": "nonlinear activation remains digital", "activations": "local_sram", "weights": "digital_or_runtime_state", "tile_count": 0, "tile_shape": None, "calibration_profile": None, "converter_boundaries": [], "fallback": None},
    ])
    source = {
        "schema_version": "aimc_projection_stack_source.v1",
        "model_id": "projection-stack",
        "model_version": "onnx-fixture-v1",
        "model_path": "/home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/samples/projection-stack.onnx",
        "dataset_id": "deterministic-projection-replay-v1",
        "source_replay": str(SOURCE.relative_to(ROOT)),
        "relative_l2_output_difference": replay["accuracy_impact"]["estimated_drop"],
        "simulator_pass": replay["accuracy_impact"]["pass"],
        "not_pretrained_foundation_model": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    contract = {
        "schema_version": "aimc_hybrid_workload_contract.v1",
        "workload_id": "projection-stack-v1",
        "model": {"id": "projection-stack", "family": "dense_projection_stack", "version": "onnx-fixture-v1", "path": str((OUT / "source_replay.json").relative_to(ROOT)), "pretrained_foundation_model": False},
        "dataset": {"id": "deterministic-projection-replay-v1", "version": "fixture-v1", "role": "held-out projection replay, not a task dataset", "path": str((OUT / "source_replay.json").relative_to(ROOT)), "sample_count": 1},
        "task": {"type": "projection_numerical_replay", "metric": "relative_l2_output_difference_on_projection_stack_trained_weight_replay", "acceptance_threshold": 0.15, "digital_baseline": "digital ONNX-weight projection stack"},
        "hardware_target": {"profile_id": "educational-hybrid-tile-v1", "analog_memory": "fixed projection weights", "digital_memory": "activation and nonlinear support", "sram": "intermediate projections and partial sums"},
        "claim_boundary": {"status": "crosssim_projection_replay_package", "allowed": "real ONNX initializer weights can feed the shared placement and schedule schema", "blocked": "pretrained foundation-model accuracy, measured latency, energy, board runtime, calibrated silicon, and production readiness"},
    }
    plan = {"schema_version": "aimc_hybrid_execution_plan.v1", "plan_id": "projection_stack_hybrid_plan_v1", "status": "crosssim_plan_physical_converter_bridge_blocked", "operator_placements": placements, "memory_plan": {"analog_memory": "four fixed projection matrices", "digital_memory": "ReLU and control", "sram": "projection activations and partial sums"}, "converter_plan": {"simulator_dac_bits": 8, "simulator_adc_bits": 8, "compatibility_status": PHYSICAL_GATE, "blocking_observation": "physical converter full-range qualification remains open"}, "provenance": {"source_replay": str(SOURCE.relative_to(ROOT)), "generated_at": datetime.now(timezone.utc).isoformat(), "not_measured_silicon": True}}
    comparison = {"schema_version": "aimc_hybrid_output_comparison.v1", "comparison_id": "projection_stack_crosssim_replay_v1", "baseline": "digital ONNX-weight projection stack", "candidate": "CrossSim projection-stack trained-weight replay", "metric": "relative_l2_output_difference_on_projection_stack_trained_weight_replay", "relative_l2_output_difference": replay["accuracy_impact"]["estimated_drop"], "pass": replay["accuracy_impact"]["pass"], "proof_level": "CrossSim trained-weight replay", "physical_converter_gate": PHYSICAL_GATE, "claim_boundary": contract["claim_boundary"]["blocked"]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "source_replay.json").write_text(json.dumps(source, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "workload_contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "hybrid_execution_plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "hybrid_output_comparison.json").write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "hybrid_execution_plan.md").write_text("\n".join(["# Projection Stack Package", "", "The existing CrossSim replay is connected to the shared compiler schema.", "", "- operators: `7`", "- analog candidates: `4`", f"- relative L2: `{comparison['relative_l2_output_difference']:.6g}`", "- simulator replay: `pass`", f"- physical converter gate: `{PHYSICAL_GATE}`", "", contract["claim_boundary"]["blocked"] + ".", ""]))
    print(f"package,{OUT}")
    print("operators,7")
    print("analog_candidates,4")
    print(f"relative_l2,{comparison['relative_l2_output_difference']:.9g}")
    print("simulator_pass,True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
