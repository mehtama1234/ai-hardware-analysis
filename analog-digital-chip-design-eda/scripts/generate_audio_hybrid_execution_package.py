#!/usr/bin/env python3
"""Generate a workload-aware hybrid plan for the wake-word MLP."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence" / "aimc-hardware-lab" / "audio-workload-v1"
OUT = ROOT / "evidence" / "aimc-hybrid-audio-workload"


def read(name: str) -> dict:
    return json.loads((SOURCE / name).read_text(encoding="utf-8"))


def main() -> int:
    contract_source = read("workload-contract.json")
    task = read("wake-nonwake-task-evaluation-v1.json")
    cost = read("wake-nonwake-end-to-end-cost-v1.json")
    analog_error = read("wake-nonwake-analog-error-evaluation-v1.json")
    rows = [
        {
            "operator_id": "feature_extraction",
            "operator": "audio_feature_extraction",
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
            "reason": "feature extraction is a signal-processing boundary and is not a weight-stationary array operation",
        },
        {
            "operator_id": "dense1.matmul",
            "operator": "MatMul",
            "placement": "digital_support",
            "candidate_placement": "analog_memory",
            "weights": "digital_sram",
            "activations": "local_sram",
            "partial_sums": "digital_accumulator",
            "weight_shape_in_out": [4, 2],
            "tile_shape": [4, 4],
            "tile_count": 1,
            "bit_slices": 2,
            "converter_boundaries": [],
            "calibration_profile": "wake-nonwake-analog-error-evaluation-v1",
            "fallback": "digital_matmul_reference",
            "analog_candidate": True,
            "reason": "task quality passes the nominal analog rehearsal, but converter boundary cost makes this small workload slower and slightly higher energy than digital",
            "cost_decision": cost["comparison"]["decision"],
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
            "candidate_placement": "analog_memory",
            "weights": "digital_sram",
            "activations": "local_sram",
            "partial_sums": "digital_accumulator",
            "weight_shape_in_out": [2, 2],
            "tile_shape": [4, 4],
            "tile_count": 1,
            "bit_slices": 2,
            "converter_boundaries": [],
            "calibration_profile": None,
            "fallback": "digital_matmul_reference",
            "analog_candidate": True,
            "reason": "small output projection does not amortize converter overhead",
            "cost_decision": cost["comparison"]["decision"],
        },
        {
            "operator_id": "decision_threshold",
            "operator": "threshold",
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
            "reason": "false-accept and false-reject decision remains independent digital control",
        },
    ]
    contract = {
        "schema_version": "aimc_hybrid_workload_contract.v1",
        "workload_id": contract_source["workload_id"],
        "model": {"id": contract_source["model"]["model_id"], **contract_source["model"], "version": "generated-rehearsal-v1", "path": "evidence/aimc-hardware-lab/audio-workload-v1/wake-nonwake-mlp.onnx"},
        "dataset": {**contract_source["dataset"], "path": "evidence/aimc-hardware-lab/audio-workload-v1/wake-nonwake-features-v1.json"},
        "task": {"type": contract_source["task"]["task_type"], "metric": contract_source["task"]["primary_metric"], "acceptance_threshold": contract_source["task"]["metric_tolerance"], "digital_baseline": "digital wake-nonwake MLP reference"},
        "hardware_target": {"analog_memory": "candidate fixed-weight dense MatMuls, subject to cost governor", "digital_memory": "feature extraction, bias, activation, decision, and fallback", "sram": "feature vectors, hidden activations, weights, partial sums, and fallback buffers", "profile_id": "educational-hybrid-tile-v1"},
        "claim_boundary": {"status": "model_backed_audio_rehearsal", "allowed": "compiler placement can retain an analog candidate while selecting digital execution when end-to-end cost is unfavorable", "blocked": "field wake-word accuracy, measured board runtime, measured power, calibrated silicon, and production readiness"},
    }
    plan = {
        "schema_version": "aimc_hybrid_execution_plan.v1",
        "plan_id": "wake_nonwake_audio_hybrid_plan_v1",
        "status": "model_backed_task_pass_digital_cost_selection_physical_converter_blocked",
        "operator_placements": rows,
        "memory_plan": {"analog_memory": "no selected operators at this workload size; dense MatMuls remain analog candidates", "digital_memory": "all selected execution including feature extraction and dense layers", "sram": "features, hidden activations, partial sums, calibration metadata, and fallback buffers"},
        "converter_plan": {"simulator_dac_bits": analog_error["analog_profile"]["dac_bits"], "simulator_adc_bits": analog_error["analog_profile"]["adc_bits"], "physical_diagnostic_bits": 4, "compatibility_status": "blocked_sar_source_common_mode", "selection_status": "digital_for_this_small_workload", "selection_reason": cost["comparison"]["reason"]},
        "task_result": {"metric": task["metric_name"], "baseline": task["baseline_metric"], "candidate": task["candidate_metric"], "pass": task["pass"], "sample_count": task["sample_count"], "false_accepts": task["false_accepts"], "false_rejects": task["false_rejects"]},
        "cost_result": cost["comparison"],
        "provenance": {"workload_contract": "evidence/aimc-hardware-lab/audio-workload-v1/workload-contract.json", "task_evaluation": "evidence/aimc-hardware-lab/audio-workload-v1/wake-nonwake-task-evaluation-v1.json", "cost_evaluation": "evidence/aimc-hardware-lab/audio-workload-v1/wake-nonwake-end-to-end-cost-v1.json", "generated_at": datetime.now(timezone.utc).isoformat(), "not_measured_silicon": True},
    }
    comparison = {
        "schema_version": "aimc_hybrid_output_comparison.v1",
        "comparison_id": "wake_nonwake_audio_task_rehearsal_v1",
        "baseline": "digital wake-nonwake MLP reference",
        "candidate": "analog dense-layer rehearsal with digital remainder and fallback",
        "metric": task["metric_name"],
        "baseline_metric": task["baseline_metric"],
        "candidate_metric": task["candidate_metric"],
        "relative_l2_output_difference": None,
        "task_metric_drop": analog_error["metric_drop"],
        "threshold": task["tolerance"],
        "pass": bool(task["pass"]),
        "proof_level": "model-backed generated-audio task rehearsal",
        "physical_converter_gate": "blocked_sar_source_common_mode",
        "claim_boundary": "task rehearsal only; does not prove field data accuracy, board runtime, measured energy, or silicon",
        "source": "evidence/aimc-hardware-lab/audio-workload-v1/wake-nonwake-task-evaluation-v1.json",
    }
    report = "\n".join([
        "# Wake-Word Hybrid Execution Plan", "",
        "This package runs the wake-word workload through the shared compiler schema and records a digital placement decision even though the dense layers are analog candidates.", "",
        f"- operators: `{len(rows)}`", f"- selected analog operators: `0`", f"- analog candidates retained for review: `{sum(row.get('analog_candidate', False) for row in rows)}`", f"- task result: `{task['metric_name']}={task['candidate_metric']}` on `{task['sample_count']}` generated samples", f"- cost decision: `{cost['comparison']['decision']}`", "- physical converter gate: `blocked_sar_source_common_mode`", "",
        "## Decision", "", "The nominal analog error rehearsal preserves all wake/nonwake decisions, but the end-to-end cost model selects the digital path: hybrid latency is 41 versus 28 normalized units and hybrid energy is 154.2 versus 152.0. This is an explicit workload-dependent fallback decision, not evidence that analog is universally unsuitable.", "", "## Claim Boundary", "", "The workload uses generated audio rather than a field dataset and has no board or silicon trace. The package proves placement reasoning and task/cost handoff only.", "",
    ])
    OUT.mkdir(parents=True, exist_ok=True)
    for name, payload in {"workload_contract.json": contract, "hybrid_execution_plan.json": plan, "hybrid_output_comparison.json": comparison}.items():
        (OUT / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "hybrid_execution_plan.md").write_text(report, encoding="utf-8")
    print(f"audio_package,{OUT}")
    print(f"operators,{len(rows)}")
    print("selected_analog_operators,0")
    print(f"analog_candidates,{sum(row.get('analog_candidate', False) for row in rows)}")
    print(f"task_pass,{task['pass']}")
    print(f"cost_decision,{cost['comparison']['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
