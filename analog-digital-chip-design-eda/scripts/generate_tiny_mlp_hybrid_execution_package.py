#!/usr/bin/env python3
"""Generate the shared compiler-schema package for the tiny MLP task rehearsal."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence" / "aimc-hardware-lab"
OUT = ROOT / "evidence" / "aimc-hybrid-tiny-mlp-task"
PHYSICAL_GATE = "blocked_sar_source_common_mode"


def read(name: str) -> dict:
    return json.loads((SOURCE / name).read_text(encoding="utf-8"))


def main() -> int:
    task = read("tiny-mlp-task-evaluation-v1.json")
    bridge = read("tiny-mlp-task-governor-bridge-v1.json")
    rows = [
        {
            "operator_id": "dense1.matmul",
            "operator": "MatMul",
            "placement": "digital_support",
            "candidate_placement": "analog_memory",
            "weights": "digital_sram",
            "activations": "local_sram",
            "partial_sums": "digital_accumulator",
            "weight_shape_in_out": [4, 4],
            "tile_shape": [16, 16],
            "tile_count": 1,
            "bit_slices": 2,
            "converter_boundaries": [],
            "calibration_profile": "tiny-mlp-task-analog-error-v1",
            "fallback": "digital_matmul_reference",
            "analog_candidate": True,
            "reason": "task rehearsal permits bounded analog service, but the physical converter gate is blocked and the current workload must use digital fallback",
            "governor_decision": bridge["governor_decision"],
        },
        {
            "operator_id": "dense1.bias",
            "operator": "Add",
            "placement": "digital_support",
            "weights": "digital_sram",
            "activations": "local_sram",
            "partial_sums": "digital_accumulator",
            "tile_shape": None,
            "tile_count": 0,
            "bit_slices": 0,
            "converter_boundaries": [],
            "calibration_profile": None,
            "fallback": None,
            "reason": "bias correction remains digital",
        },
        {
            "operator_id": "dense1.relu",
            "operator": "Relu",
            "placement": "digital_support",
            "weights": "none",
            "activations": "local_sram",
            "partial_sums": "digital_accumulator",
            "tile_shape": None,
            "tile_count": 0,
            "bit_slices": 0,
            "converter_boundaries": [],
            "calibration_profile": None,
            "fallback": None,
            "reason": "nonlinear activation remains digital",
        },
        {
            "operator_id": "dense2.matmul",
            "operator": "MatMul",
            "placement": "digital_support",
            "candidate_placement": "digital_support",
            "weights": "digital_sram",
            "activations": "local_sram",
            "partial_sums": "digital_accumulator",
            "weight_shape_in_out": [2, 2],
            "tile_shape": [16, 16],
            "tile_count": 1,
            "bit_slices": 0,
            "converter_boundaries": [],
            "calibration_profile": None,
            "fallback": None,
            "reason": "downstream projection remains exact digital support in this isolated task experiment",
        },
        {
            "operator_id": "dense2.bias",
            "operator": "Add",
            "placement": "digital_support",
            "weights": "digital_sram",
            "activations": "local_sram",
            "partial_sums": "digital_accumulator",
            "tile_shape": None,
            "tile_count": 0,
            "bit_slices": 0,
            "converter_boundaries": [],
            "calibration_profile": None,
            "fallback": None,
            "reason": "bias correction remains digital",
        },
        {
            "operator_id": "classification_decision",
            "operator": "ArgMax",
            "placement": "digital_support",
            "weights": "none",
            "activations": "local_sram",
            "partial_sums": "digital_accumulator",
            "tile_shape": None,
            "tile_count": 0,
            "bit_slices": 0,
            "converter_boundaries": [],
            "calibration_profile": None,
            "fallback": None,
            "reason": "task decision remains independent digital control",
        },
    ]
    contract = {
        "schema_version": "aimc_hybrid_workload_contract.v1",
        "workload_id": "tiny_mlp_task_hybrid_vertical_slice_v1",
        "model": {"id": "tiny-mlp", "version": "synthetic-rehearsal-v1", "path": "ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/samples/tiny-mlp.onnx", "family": "small fixed-weight MLP task rehearsal", "pretrained_foundation_model": False},
        "dataset": {"id": task["dataset_id"], "version": task["dataset_version"], "role": "synthetic binary feature task rehearsal", "sample_count": task["sample_count"]},
        "task": {"type": "binary feature classification", "metric": task["metric_name"], "acceptance_threshold": task["tolerance"], "digital_baseline": "digital tiny MLP reference"},
        "hardware_target": {"analog_memory": "dense1 fixed-weight MatMul candidate", "digital_memory": "bias, activation, downstream projection, decision, calibration, and fallback", "sram": "features, activations, partial sums, and fallback buffers", "profile_id": "educational-hybrid-tile-v1"},
        "claim_boundary": {"status": "model_backed_synthetic_task_rehearsal", "allowed": "the task metric can inform a bounded analog placement and governor decision", "blocked": "real customer-data accuracy, physical converter acceptance, board runtime, measured power, calibrated silicon, and production readiness"},
    }
    plan = {
        "schema_version": "aimc_hybrid_execution_plan.v1",
        "plan_id": "tiny_mlp_task_hybrid_plan_v1",
        "status": "task_rehearsal_pass_digital_fallback_physical_converter_blocked",
        "operator_placements": rows,
        "memory_plan": {"analog_memory": "dense1.matmul candidate only", "digital_memory": "all selected execution and task decision", "sram": "features, hidden activations, partial sums, calibration metadata, and fallback buffers"},
        "converter_plan": {"simulator_dac_bits": 4, "simulator_adc_bits": 6, "physical_diagnostic_bits": 4, "compatibility_status": PHYSICAL_GATE, "selection_status": "digital_fallback_until_physical_converter_passes"},
        "task_result": {"metric": task["metric_name"], "baseline": task["baseline_metric"], "candidate": task["candidate_metric"], "drop": task["metric_drop"], "pass": task["pass"], "sample_count": task["sample_count"]},
        "governor_result": {"decision": bridge["governor_decision"], "action": bridge["governor_action"], "reason": bridge["governor_reason"], "residual_q8": bridge["residual_q8"], "sensitivity_q8": bridge["sensitivity_q8"]},
        "provenance": {"task_evaluation": "evidence/aimc-hardware-lab/tiny-mlp-task-evaluation-v1.json", "governor_bridge": "evidence/aimc-hardware-lab/tiny-mlp-task-governor-bridge-v1.json", "generated_at": datetime.now(timezone.utc).isoformat(), "not_measured_silicon": True},
    }
    comparison = {
        "schema_version": "aimc_hybrid_output_comparison.v1",
        "comparison_id": "tiny_mlp_task_rehearsal_v1",
        "baseline": "digital tiny MLP reference",
        "candidate": "bounded analog dense1 rehearsal with digital remainder",
        "metric": task["metric_name"],
        "relative_l2_output_difference": None,
        "baseline_metric": task["baseline_metric"],
        "candidate_metric": task["candidate_metric"],
        "task_metric_drop": task["metric_drop"],
        "threshold": task["tolerance"],
        "pass": bool(task["pass"]),
        "proof_level": "model-backed synthetic task rehearsal",
        "physical_converter_gate": PHYSICAL_GATE,
        "claim_boundary": "synthetic task rehearsal only; does not prove field-data accuracy, board runtime, measured energy, or silicon",
        "source": "evidence/aimc-hardware-lab/tiny-mlp-task-evaluation-v1.json",
    }
    report = "\n".join([
        "# Tiny MLP Task Hybrid Execution Plan", "",
        "This package puts the existing tiny MLP task and governor rehearsal into the shared compiler/runtime schema.", "",
        f"- operators: `{len(rows)}`", "- analog candidates retained: `1`", "- selected execution: `digital fallback`", f"- task result: `{task['metric_name']}={task['candidate_metric']}` versus baseline `{task['baseline_metric']}`", f"- physical converter gate: `{PHYSICAL_GATE}`", "",
        "The task rehearsal passes its provisional accuracy tolerance, but it uses synthetic data and does not justify a physical analog claim. The dense1 MatMul remains an analog candidate in the compiler record; the guarded runtime must use digital execution until the converter and source interface pass.", "",
    ])
    OUT.mkdir(parents=True, exist_ok=True)
    for name, payload in {"workload_contract.json": contract, "hybrid_execution_plan.json": plan, "hybrid_output_comparison.json": comparison}.items():
        (OUT / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "hybrid_execution_plan.md").write_text(report, encoding="utf-8")
    print(f"tiny_mlp_package,{OUT}")
    print(f"operators,{len(rows)}")
    print("analog_candidates,1")
    print("selected_analog_operators,0")
    print(f"task_pass,{task['pass']}")
    print(f"physical_converter_gate,{PHYSICAL_GATE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
