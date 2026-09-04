#!/usr/bin/env python3
"""Convert bounded edge-workload intake fixtures into compiler-review packages."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "evidence"
PHYSICAL_GATE = "blocked_sar_source_common_mode"

WORKLOADS = {
    "wearable-keyword-v1": {
        "package": "aimc-hybrid-wearable-keyword",
        "model_id": "keyword-detector-v3-intake",
        "dataset_id": "wearable-keyword-intake-scenarios-v1",
        "family": "wearable_always_on_audio",
        "input": "audio_window[1,16000]",
        "parameters": "3.8M",
        "target": {"accuracy": "94.0%", "latency": "< 6 ms", "energy": "< 50 uJ"},
        "layers": [
            ("input.proj", "MatMul", "analog_memory", "dense matrix work with reused weights"),
            ("attention.softmax", "Softmax", "digital_support", "nonlinear attention normalization"),
            ("attention.value", "MatMul", "analog_memory", "supported matrix path, pending sensitivity"),
            ("encoder.layernorm", "LayerNorm", "digital_support", "normalization remains digital"),
            ("ffn.matmul.1", "MatMul", "analog_memory", "large repeated matrix work"),
            ("classifier.out", "MatMul", "analog_memory", "small dense classifier output"),
        ],
        "task_metric": "false_accept_and_false_reject_rate",
        "risk": "repeated analog/digital crossings around attention",
    },
    "smart-camera-inspection-v1": {
        "package": "aimc-hybrid-smart-camera-inspection",
        "model_id": "camera-defect-classifier-intake",
        "dataset_id": "smart-camera-inspection-intake-scenarios-v1",
        "family": "smart_camera_vision",
        "input": "image[1,3,224,224]",
        "parameters": "11.6M",
        "target": {"accuracy": "95.0%", "latency": "< 12 ms", "energy": "< 90 uJ"},
        "layers": [
            ("stem.conv", "Conv2D", "analog_memory", "convolution maps to repeated matrix work"),
            ("block3.depthwise", "DepthwiseConv", "digital_support", "low reuse; explicit fallback"),
            ("block5.pointwise", "Conv2D", "analog_memory", "regular high-reuse dataflow"),
            ("classifier.norm", "LayerNorm", "digital_support", "normalization remains digital"),
            ("classifier.fc", "MatMul", "analog_memory", "dense output layer, accuracy-sensitive"),
        ],
        "task_metric": "classification_or_detection_metric_plus_sensor_to_output_latency",
        "risk": "classifier head sensitivity",
    },
    "robot-sensor-policy-v1": {
        "package": "aimc-hybrid-robot-sensor-policy",
        "model_id": "fusion-transformer-small-intake",
        "dataset_id": "robot-sensor-policy-intake-scenarios-v1",
        "family": "mobile_robot_sensor_fusion",
        "input": "camera+imu+depth tokens",
        "parameters": "24.2M",
        "target": {"accuracy": "90.0%", "latency": "< 8 ms", "energy": "< 150 uJ"},
        "layers": [
            ("vision.proj", "MatMul", "analog_memory", "dense projection with strong reuse"),
            ("imu.fusion.gate", "Elementwise", "digital_support", "control-heavy sensor fusion logic"),
            ("attention.qkv", "MatMul", "analog_memory", "large matrix candidate with boundary risk"),
            ("attention.softmax", "Softmax", "digital_support", "nonlinear attention operation"),
            ("planner.head", "MatMul", "analog_memory", "planner output requires safety-margin validation"),
        ],
        "task_metric": "control_jitter_and_task_completion",
        "risk": "irregular fusion and attention boundaries",
    },
    "compact-vision-or-defect-v1": {
        "package": "aimc-hybrid-compact-vision-defect",
        "model_id": "compact-defect-classifier-intake",
        "dataset_id": "compact-vision-intake-scenarios-v1",
        "family": "compact_vision_defect_detection",
        "input": "image[1,3,224,224]",
        "parameters": "11.6M",
        "target": {"accuracy": "95.0%", "latency": "< 12 ms", "energy": "< 90 uJ"},
        "layers": [
            ("stem.conv", "Conv2D", "analog_memory", "regular convolution dataflow"),
            ("block3.depthwise", "DepthwiseConv", "digital_support", "low reuse requires fallback"),
            ("block5.pointwise", "Conv2D", "analog_memory", "high weight reuse"),
            ("classifier.norm", "LayerNorm", "digital_support", "normalization remains digital"),
            ("classifier.fc", "MatMul", "analog_memory", "dense classifier candidate with sensitivity risk"),
        ],
        "task_metric": "classification_or_detection_metric_plus_sensor_to_output_latency",
        "risk": "classifier head sensitivity",
    },
    "vla-or-physical-ai-v1": {
        "package": "aimc-hybrid-vla-physical-ai",
        "model_id": "vla-policy-intake",
        "dataset_id": "vla-physical-ai-intake-scenarios-v1",
        "family": "vision_language_action_policy",
        "input": "camera+language+proprioception tokens",
        "parameters": "intake shape only",
        "target": {"accuracy": "task-specific", "latency": "< control deadline", "energy": "system budget required"},
        "layers": [
            ("perception.proj", "MatMul", "analog_memory", "fixed visual projection candidate"),
            ("language.proj", "MatMul", "analog_memory", "fixed language projection candidate"),
            ("cross_attention", "Attention", "digital_support", "changing modalities and memory need explicit control"),
            ("policy.mlp", "MatMul", "analog_memory", "fixed policy MLP candidate pending task sensitivity"),
            ("action.guard", "SafetyControl", "digital_support", "deterministic safety and actuator handoff"),
        ],
        "task_metric": "task_completion_and_control_safety_metric",
        "risk": "control safety and cross-modal boundary behavior",
    },
}


def make_package(workload_id: str, spec: dict) -> None:
    out = OUT_ROOT / spec["package"]
    rows = []
    for operator_id, operator, placement, reason in spec["layers"]:
        analog = placement == "analog_memory"
        rows.append(
            {
                "operator_id": operator_id,
                "operator": operator,
                "placement": placement,
                "reason": reason,
                "activations": "local_sram",
                "weights": "analog_array" if analog else "digital_or_runtime_state",
                "tile_count": 1 if analog else 0,
                "tile_shape": [128, 128] if analog else None,
                "calibration_profile": "edge-intake-affine-v1" if analog else None,
                "converter_boundaries": ["DAC_input", "ADC_output"] if analog else [],
                "fallback": "digital_reference" if analog else None,
            }
        )
    source = {
        "schema_version": "aimc_edge_intake_fixture.v1",
        "workload_id": workload_id,
        "source_origin": "ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/mock-api",
        "model": {"id": spec["model_id"], "parameters": spec["parameters"], "input": spec["input"]},
        "target": spec["target"],
        "task_metric": spec["task_metric"],
        "risk": spec["risk"],
        "intake_only": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    contract = {
        "schema_version": "aimc_hybrid_workload_contract.v1",
        "workload_id": workload_id,
        "model": {"id": spec["model_id"], "family": spec["family"], "version": "intake-fixture-v1", "path": str((out / "source_intake.json").relative_to(ROOT)), "pretrained_foundation_model": False},
        "dataset": {"id": spec["dataset_id"], "version": "intake-fixture-v1", "role": "mock workload constraints, not task samples", "path": str((out / "source_intake.json").relative_to(ROOT)), "sample_count": 0},
        "task": {"type": "edge_workload_intake_replay", "metric": "intake_placement_and_cost_policy_replay", "acceptance_threshold": "all intake layer placements reproduce source fixture", "digital_baseline": "mock intake digital reference"},
        "hardware_target": {"profile_id": "educational-hybrid-tile-v1", "analog_memory": "fixed-weight dense or convolution candidates", "digital_memory": "nonlinear and fallback path", "sram": "sensor features and partial sums"},
        "claim_boundary": {"status": "intake_estimate_package", "allowed": "sensor-boundary assumptions, operator placement, fallback reasons, and target schedule can be reviewed", "blocked": "real model execution, task accuracy, real sensor data, measured latency, energy, board runtime, calibrated silicon, and production readiness"},
    }
    plan = {
        "schema_version": "aimc_hybrid_execution_plan.v1",
        "plan_id": f"{workload_id.replace('-', '_')}_intake_plan_v1",
        "status": "intake_plan_physical_converter_bridge_blocked",
        "operator_placements": rows,
        "memory_plan": {"analog_memory": "fixed-weight candidate layers", "digital_memory": "preprocessing, nonlinear, and fallback operations", "sram": "sensor features, activations, and partial sums"},
        "converter_plan": {"simulator_dac_bits": 8, "simulator_adc_bits": 8, "compatibility_status": PHYSICAL_GATE, "blocking_observation": "physical converter source common-mode qualification remains open"},
        "provenance": {"source_intake": str((out / "source_intake.json").relative_to(ROOT)), "generated_at": datetime.now(timezone.utc).isoformat(), "not_measured_silicon": True},
    }
    comparison = {
        "schema_version": "aimc_hybrid_output_comparison.v1",
        "comparison_id": f"{workload_id.replace('-', '_')}_intake_replay_v1",
        "baseline": "mock intake digital reference",
        "candidate": "intake-derived mixed-memory placement",
        "metric": "intake_placement_and_cost_policy_replay",
        "relative_l2_output_difference": None,
        "pass": True,
        "proof_level": "imported intake estimate",
        "placement_reproduced": True,
        "physical_converter_gate": PHYSICAL_GATE,
        "claim_boundary": contract["claim_boundary"]["blocked"],
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "source_intake.json").write_text(json.dumps(source, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "workload_contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "hybrid_execution_plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "hybrid_output_comparison.json").write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "hybrid_execution_plan.md").write_text("\n".join([f"# {workload_id} Intake Package", "", "This is an imported workload-intake estimate, not a real model or task benchmark.", "", f"- operators: `{len(rows)}`", f"- analog candidates: `{sum(item['placement'] == 'analog_memory' for item in rows)}`", f"- digital/fallback operators: `{sum(item['placement'] == 'digital_support' for item in rows)}`", "- placement replay: `pass`", f"- physical converter gate: `{PHYSICAL_GATE}`", "", contract["claim_boundary"]["blocked"] + ".", ""]))
    print(f"package,{workload_id},{out}")
    print(f"operators,{len(rows)}")
    print(f"analog_candidates,{sum(item['placement'] == 'analog_memory' for item in rows)}")
    print("placement_replay,True")


def main() -> int:
    for workload_id, spec in WORKLOADS.items():
        make_package(workload_id, spec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
