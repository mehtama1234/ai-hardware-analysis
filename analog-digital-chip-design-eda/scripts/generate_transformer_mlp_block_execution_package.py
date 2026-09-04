#!/usr/bin/env python3
"""Generate a shared-schema package for one transformer MLP block."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "evidence" / "aimc-simulator-adapters"
OUT = ROOT / "evidence" / "aimc-hybrid-transformer-mlp-block"


def load(name: str) -> dict:
    return json.loads((SIM / name).read_text(encoding="utf-8"))


def main() -> int:
    summary = load("calibrated-transformer-mlp-block-simulator-payload-run-summary.json")
    replay = load("crosssim-calibrated-transformer-mlp-block-analog-error-simulation.json")
    assumptions = replay["error_model"]["array_assumptions"]
    shapes = dict(zip(assumptions["candidate_ids"], assumptions["candidate_shapes"]))
    analog = []
    for operator_id in summary["candidate_ids"]:
        shape = json.loads(shapes[operator_id])
        analog.append({"operator_id": operator_id, "operator": "MatMul", "placement": "analog_memory", "weights": "analog_array", "activations": "local_sram", "partial_sums": "local_sram_then_digital_accumulator", "weight_shape_in_out": shape, "tile_shape": [16, 16], "tile_count": math.ceil(shape[0] / 16) * math.ceil(shape[1] / 16), "bit_slices": 8, "converter_boundaries": ["DAC_input", "ADC_output"], "calibration_profile": "crosssim-held-out-affine-transformer-mlp-block-v0", "fallback": "digital_matmul_reference"})
    digital = [("bias.add", "Add", "bias correction remains digital"), ("activation.relu", "Relu", "nonlinear activation remains digital"), ("gated.elementwise_mul", "Mul", "elementwise gating remains digital"), ("residual.add", "Add", "residual routing remains digital")]
    rows = analog + [{"operator_id": op, "operator": kind, "placement": "digital_support", "weights": "none_or_digital_buffer", "activations": "local_sram", "partial_sums": "digital_accumulator", "tile_shape": None, "tile_count": 0, "bit_slices": 0, "converter_boundaries": [], "calibration_profile": None, "fallback": None, "reason": reason} for op, kind, reason in digital]
    contract = {"schema_version": "aimc_hybrid_workload_contract.v1", "workload_id": "transformer_mlp_block_hybrid_vertical_slice_v1", "model": {"id": "transformer-mlp-block", "version": "fixture-v1", "path": summary["source_model"], "family": "single transformer-style MLP block", "pretrained_foundation_model": False}, "dataset": {"id": "deterministic-mlp-block-held-out-v1", "version": "fixture-v1", "role": "held-out vector replay, not a task dataset", "sample_count": 1}, "task": {"type": "transformer MLP numerical replay", "metric": replay["accuracy_impact"]["metric"], "acceptance_threshold": 0.15, "digital_baseline": "digital ONNX-weight transformer MLP block"}, "hardware_target": {"analog_memory": "four fixed-weight MatMuls", "digital_memory": "bias, nonlinear, residual, calibration, and fallback", "sram": "activations and partial sums", "profile_id": "educational-hybrid-tile-v1"}, "claim_boundary": {"status": "calibrated_simulator_vertical_slice_only", "allowed": "calibrated CrossSim replay of a fixed-weight transformer MLP block", "blocked": "pretrained token accuracy, physical converter acceptance, board runtime, measured energy, and silicon"}}
    plan = {"schema_version": "aimc_hybrid_execution_plan.v1", "plan_id": "transformer_mlp_block_hybrid_plan_v1", "status": "simulator_plan_physical_converter_bridge_blocked", "operator_placements": rows, "memory_plan": {"analog_memory": "four fixed-weight MatMuls", "digital_memory": "bias, nonlinear, residual, calibration, and fallback", "sram": "inter-operator activations and partial sums"}, "converter_plan": {"simulator_dac_bits": replay["error_model"]["dac_bits"], "simulator_adc_bits": replay["error_model"]["adc_bits"], "physical_diagnostic_bits": 4, "compatibility_status": "blocked_sar_source_common_mode", "blocking_observation": "nominal DAC transfer passes, but coupled SAR source common-mode and endpoint headroom remain unresolved"}, "provenance": {"source_model": summary["source_model"], "calibrated_summary": "evidence/aimc-simulator-adapters/calibrated-transformer-mlp-block-simulator-payload-run-summary.json", "generated_at": datetime.now(timezone.utc).isoformat(), "not_measured_silicon": True}}
    comparison = {"schema_version": "aimc_hybrid_output_comparison.v1", "comparison_id": "transformer_mlp_block_crosssim_held_out_v1", "baseline": "digital ONNX-weight transformer MLP block", "candidate": "CrossSim calibrated analog MatMuls plus digital support", "metric": replay["accuracy_impact"]["metric"], "relative_l2_output_difference": replay["accuracy_impact"]["estimated_drop"], "threshold": 0.15, "pass": bool(replay["accuracy_impact"]["pass"]), "proof_level": "calibrated simulator replay", "physical_converter_gate": "blocked_sar_source_common_mode", "claim_boundary": "fixture replay only; not task, board, energy, or silicon evidence", "source": "evidence/aimc-simulator-adapters/crosssim-calibrated-transformer-mlp-block-analog-error-simulation.json"}
    report = "\n".join(["# Transformer MLP Block Hybrid Execution Plan", "", "A single transformer-style MLP block with four fixed-weight MatMuls mapped to analog memory and bias, nonlinear, gating, residual, calibration, and fallback operations kept digital.", "", f"- analog operators: `{len(analog)}`", f"- digital support operators: `{len(digital)}`", f"- calibrated CrossSim relative L2: `{comparison['relative_l2_output_difference']:.6g}`", "- physical converter gate: `blocked_sar_source_common_mode`", "", "This is a deterministic fixture replay, not pretrained transformer token accuracy or hardware evidence.", ""])
    OUT.mkdir(parents=True, exist_ok=True)
    for name, payload in {"workload_contract.json": contract, "hybrid_execution_plan.json": plan, "hybrid_output_comparison.json": comparison, "analog_error_replay.json": replay}.items():
        (OUT / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "hybrid_execution_plan.md").write_text(report, encoding="utf-8")
    print(f"mlp_block_package,{OUT}")
    print("analog_operators,4")
    print("digital_support_operators,4")
    print(f"simulator_relative_l2,{comparison['relative_l2_output_difference']:.9g}")
    print(f"simulator_pass,{comparison['pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
