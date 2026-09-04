#!/usr/bin/env python3
"""Generate the first auditable hybrid transformer execution package."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "evidence" / "aimc-simulator-adapters" / "calibrated-deep-transformer-mlp-stack-simulator-payload-run-summary.json"
CROSSSIM = ROOT / "evidence" / "aimc-simulator-adapters" / "crosssim-calibrated-deep-transformer-mlp-stack-analog-error-simulation.json"
OUT = ROOT / "evidence" / "aimc-hybrid-transformer-vertical-slice"
PHYSICAL_GATE = "blocked_sar_source_common_mode"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def tile_count(shape: list[int], tile: int = 16) -> int:
    return math.ceil(shape[0] / tile) * math.ceil(shape[1] / tile)


def build_contract(summary: dict) -> dict:
    return {
        "schema_version": "aimc_hybrid_workload_contract.v1",
        "workload_id": "deep_transformer_mlp_stack_vertical_slice_v1",
        "model": {
            "id": "deep-transformer-mlp-stack",
            "version": "fixture-v1",
            "path": summary["source_model"],
            "family": "three-block transformer-style MLP fixture",
            "pretrained_foundation_model": False,
        },
        "dataset": {
            "id": "deterministic-held-out-replay-v1",
            "version": "fixture-v1",
            "role": "held-out vector replay, not a task dataset",
            "sample_count": 1,
        },
        "task": {
            "type": "hybrid transformer-MLP numerical replay",
            "metric": "relative_l2_output_difference",
            "acceptance_threshold": 0.15,
            "digital_baseline": "digital ONNX-weight execution",
        },
        "hardware_target": {
            "analog_memory": "fixed-weight matrix multiply candidates",
            "digital_memory": "digital correction, nonlinear, residual, control, and fallback path",
            "sram": "activations, partial sums, calibration values, and fallback buffers",
            "profile_id": "educational-hybrid-tile-v1",
        },
        "claim_boundary": {
            "status": "simulator_vertical_slice_only",
            "allowed": "a calibrated simulator replay can preserve the fixture output under the stated assumptions",
            "blocked": "pretrained transformer accuracy, calibrated silicon, board runtime, measured power, and production readiness",
        },
    }


def build_execution_plan(summary: dict) -> dict:
    shapes = dict(zip(summary["candidate_ids"], summary["results"][0].get("candidate_shapes", [])))
    # The summary stores candidate shapes in each simulator payload, not at its top level.
    if not shapes:
        payload = load(CROSSSIM)
        candidates = payload["error_model"]["array_assumptions"]
        shapes = dict(zip(candidates["candidate_ids"], candidates["candidate_shapes"]))

    rows = []
    for candidate_id in summary["candidate_ids"]:
        shape = json.loads(shapes[candidate_id]) if isinstance(shapes[candidate_id], str) else shapes[candidate_id]
        rows.append(
            {
                "operator_id": candidate_id,
                "operator": "MatMul",
                "placement": "analog_memory",
                "weights": "analog_array",
                "activations": "local_sram",
                "partial_sums": "local_sram_then_digital_accumulator",
                "weight_shape_in_out": shape,
                "tile_shape": [16, 16],
                "tile_count": tile_count(shape),
                "bit_slices": 1,
                "converter_boundaries": ["DAC_input", "ADC_output"],
                "calibration_profile": "crosssim-held-out-affine-deep-transformer-mlp-stack-v0",
                "fallback": "digital_matmul_reference",
                "residual_budget_relative_l2": 0.15,
            }
        )

    digital = [
        ("bias.add", "Add", "digital_support", "bias correction is not a weight-stationary array operation"),
        ("activation.relu", "Relu", "digital_support", "nonlinear function remains outside the analog tile"),
        ("gated.elementwise_mul", "Mul", "digital_support", "elementwise gating is kept digital"),
        ("residual.add", "Add", "digital_support", "residual routing and accumulation remain digital"),
    ]
    for operator_id, operator, placement, reason in digital:
        rows.append(
            {
                "operator_id": operator_id,
                "operator": operator,
                "placement": placement,
                "weights": "none_or_digital_buffer",
                "activations": "local_sram",
                "partial_sums": "digital_accumulator",
                "tile_shape": None,
                "tile_count": 0,
                "bit_slices": 0,
                "converter_boundaries": [],
                "calibration_profile": None,
                "fallback": None,
                "reason": reason,
            }
        )

    return {
        "schema_version": "aimc_hybrid_execution_plan.v1",
        "plan_id": "deep_transformer_mlp_stack_hybrid_plan_v1",
        "status": "simulator_plan_physical_converter_bridge_blocked",
        "operator_placements": rows,
        "memory_plan": {
            "analog_memory": "12 fixed-weight MatMul operators",
            "digital_memory": "correction, nonlinear, residual, control, and fallback operations",
            "sram": "all inter-operator activations, partial sums, calibration values, and fallback buffers",
        },
        "converter_plan": {
            "simulator_dac_bits": 8,
            "simulator_adc_bits": 8,
            "physical_diagnostic_bits": 4,
            "physical_measurement_ns": 9.0,
            "physical_topology": "differential break-before-make with 4x top-plate dummy capacitance",
            "compatibility_status": PHYSICAL_GATE,
            "blocking_observation": "nominal DAC transfer passes, but level-shifted physical SAR returns only 2/5 representative conversions and the source interface has not closed the endpoint headroom contract",
        },
        "provenance": {
            "source_model": summary["source_model"],
            "calibrated_summary": str(SUMMARY.relative_to(ROOT)),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "not_measured_silicon": True,
        },
    }


def build_comparison(crosssim: dict) -> dict:
    impact = crosssim["accuracy_impact"]
    return {
        "schema_version": "aimc_hybrid_output_comparison.v1",
        "comparison_id": "deep_transformer_mlp_stack_crosssim_held_out_v1",
        "baseline": "digital ONNX-weight deep transformer MLP stack",
        "candidate": "CrossSim calibrated analog MatMul plus digital nonlinear/residual path",
        "metric": impact["metric"],
        "relative_l2_output_difference": impact["estimated_drop"],
        "threshold": impact.get("pass") and 0.15 or 0.15,
        "pass": bool(impact["pass"]),
        "proof_level": "calibrated simulator replay",
        "physical_converter_gate": PHYSICAL_GATE,
        "claim_boundary": "passes the named software fixture replay only; does not prove task accuracy, silicon, board runtime, or measured energy",
        "source": str(CROSSSIM.relative_to(ROOT)),
    }


def build_bit_slicing_plan(plan: dict) -> dict:
    analog_rows = [row for row in plan["operator_placements"] if row["placement"] == "analog_memory"]
    return {
        "schema_version": "aimc_bit_slicing_plan.v1",
        "plan_id": "deep_transformer_mlp_stack_bit_slicing_v1",
        "logical_weight_bits": 8,
        "physical_cell_bits": 1,
        "slice_count": 8,
        "slice_significance": "least_significant_slice_first",
        "programming_range": "normalized_signed_weight_per_slice",
        "read_order": "one_slice_per_analog_read_then_digital_recombine",
        "per_slice_adc_bits": 8,
        "partial_sum_width_bits": 24,
        "overflow_margin": "must be checked against tile_count and activation range before hardware execution",
        "operator_ids": [row["operator_id"] for row in analog_rows],
        "physical_converter_compatibility": PHYSICAL_GATE,
        "claim_boundary": "mapping rule only; does not prove physical cell precision or converter acceptance",
    }


def write_report(contract: dict, plan: dict, comparison: dict) -> None:
    analog = sum(row["placement"] == "analog_memory" for row in plan["operator_placements"])
    digital = sum(row["placement"] == "digital_support" for row in plan["operator_placements"])
    lines = [
        "# Hybrid Transformer Vertical Slice",
        "",
        "This package connects one three-block transformer-style MLP fixture to an explicit analog-memory, digital-support, and SRAM execution plan.",
        "",
        f"- analog operators: `{analog}`",
        f"- digital support operators: `{digital}`",
        "- activations and partial sums: `local SRAM`",
        f"- simulator output comparison: `{comparison['relative_l2_output_difference']:.6g}` relative L2, pass `{str(comparison['pass']).lower()}`",
        "- execution handoff: `run_hybrid_transformer_vertical_slice.py` validates the plan and emits the operator-level replay trace",
        f"- physical converter gate: `{PHYSICAL_GATE}`",
        "",
        "## What This Proves",
        "",
        "The calibrated CrossSim replay preserves the output of this deterministic fixture under its stated simulator assumptions. The execution plan makes the mixed-memory boundary explicit: fixed-weight MatMuls are analog candidates, while bias, nonlinear, residual, control, calibration, and fallback work remains digital with SRAM buffering.",
        "",
        "## What It Does Not Prove",
        "",
        "This is not pretrained transformer accuracy, a full attention execution, measured silicon, board runtime, measured power, thermal behavior, or production readiness. The physical Sky130 converter is not yet compatible with the simulator's 8-bit converter assumption because its corrected 4-bit high-code spacing is insufficient.",
        "",
        "## Next Gate",
        "",
        "Repair or replace the physical converter topology, then rerun the same plan with a converter profile that matches the analog simulator. After that, add the attention-shaped fixture while keeping dynamic attention selection, Softmax, normalization, KV-cache movement, and token decisions on the digital/SRAM path.",
        "",
    ]
    (OUT / "hybrid_execution_plan.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    summary = load(SUMMARY)
    crosssim = load(CROSSSIM)
    OUT.mkdir(parents=True, exist_ok=True)
    contract = build_contract(summary)
    plan = build_execution_plan(summary)
    comparison = build_comparison(crosssim)
    bit_slicing = build_bit_slicing_plan(plan)
    for name, payload in {
        "workload_contract.json": contract,
        "hybrid_execution_plan.json": plan,
        "bit_slicing_plan.json": bit_slicing,
        "hybrid_output_comparison.json": comparison,
        "analog_error_replay.json": crosssim,
    }.items():
        (OUT / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(contract, plan, comparison)
    print(f"hybrid_package,{OUT}")
    print(f"analog_operators,{sum(row['placement'] == 'analog_memory' for row in plan['operator_placements'])}")
    print(f"digital_support_operators,{sum(row['placement'] == 'digital_support' for row in plan['operator_placements'])}")
    print(f"simulator_relative_l2,{comparison['relative_l2_output_difference']:.9g}")
    print(f"simulator_pass,{comparison['pass']}")
    print(f"physical_converter_gate,{plan['converter_plan']['compatibility_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
