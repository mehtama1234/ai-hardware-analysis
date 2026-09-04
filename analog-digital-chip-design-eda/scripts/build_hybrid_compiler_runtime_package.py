#!/usr/bin/env python3
"""Build one compiler/runtime handoff from the two hybrid model slices."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    "tiny_mlp_task": ROOT / "evidence" / "aimc-hybrid-tiny-mlp-task",
    "projection_stack": ROOT / "evidence" / "aimc-hybrid-projection-stack",
    "deep_transformer_mlp_stack": ROOT / "evidence" / "aimc-hybrid-transformer-vertical-slice",
    "attention_block": ROOT / "evidence" / "aimc-hybrid-transformer-attention-slice",
    "transformer_mlp_block": ROOT / "evidence" / "aimc-hybrid-transformer-mlp-block",
    "wake_nonwake_audio": ROOT / "evidence" / "aimc-hybrid-audio-workload",
    "small_language_model_serving": ROOT / "evidence" / "aimc-hybrid-language-model-serving",
    "wearable_keyword": ROOT / "evidence" / "aimc-hybrid-wearable-keyword",
    "smart_camera_inspection": ROOT / "evidence" / "aimc-hybrid-smart-camera-inspection",
    "robot_sensor_policy": ROOT / "evidence" / "aimc-hybrid-robot-sensor-policy",
    "compact_vision_defect": ROOT / "evidence" / "aimc-hybrid-compact-vision-defect",
    "vla_physical_ai": ROOT / "evidence" / "aimc-hybrid-vla-physical-ai",
}
OUT = ROOT / "evidence" / "aimc-hybrid-compiler-runtime"
HARDWARE_PROFILE = ROOT / "evidence" / "aimc-hardware-lab" / "hardware-profile-educational-hybrid-tile-v1.json"
PHYSICAL_GATE = "blocked_sar_source_common_mode"
PORTFOLIO_IDS = {
    "tiny_mlp_task": "tiny-mlp-task-v1",
    "projection_stack": "projection-stack-v1",
    "deep_transformer_mlp_stack": "deep-transformer-mlp-stack-v1",
    "attention_block": "attention-block-v1",
    "transformer_mlp_block": "transformer-mlp-block-v1",
    "wake_nonwake_audio": "wake-nonwake-audio-v1",
    "small_language_model_serving": "small-language-model-serving-v1",
    "wearable_keyword": "wearable-keyword-v1",
    "smart_camera_inspection": "smart-camera-inspection-v1",
    "robot_sensor_policy": "robot-sensor-policy-v1",
    "compact_vision_defect": "compact-vision-or-defect-v1",
    "vla_physical_ai": "vla-or-physical-ai-v1",
}


def read(package: Path, name: str) -> dict:
    return json.loads((package / name).read_text(encoding="utf-8"))


def build_model_entry(model_id: str, package: Path) -> tuple[dict, list[dict]]:
    contract = read(package, "workload_contract.json")
    plan = read(package, "hybrid_execution_plan.json")
    plan["converter_plan"]["compatibility_status"] = PHYSICAL_GATE
    plan["converter_plan"]["blocking_observation"] = "nominal differential DAC transfer passes, but physical SAR source common-mode and input-range qualification remains open"
    comparison = read(package, "hybrid_output_comparison.json")
    rows = plan["operator_placements"]
    if not rows:
        raise SystemExit(f"{model_id}: execution plan has no operators")
    events = []
    for row in rows:
        operator_id = row["operator_id"]
        if row["placement"] == "analog_memory":
            steps = [
                ("activation_load", "local_sram", "load activation or token state"),
                ("dac_encode", "converter_boundary", "encode analog-array input"),
                ("analog_tile_compute", "analog_memory", "execute assigned analog tile(s)"),
                ("adc_decode", "converter_boundary", "digitize analog result"),
                ("calibration_apply", "digital_support", row["calibration_profile"]),
                ("partial_sum_store", "local_sram", "store corrected partial sum"),
            ]
        else:
            steps = [("digital_support", "digital_memory_and_sram", row.get("reason", "digital support operation"))]
        for event, location, detail in steps:
            events.append({"model_id": model_id, "operator_id": operator_id, "event": event, "location": location, "detail": detail})
    entry = {
        "model_id": contract["model"]["id"],
        "workload_id": contract["workload_id"],
        "portfolio_workload_id": PORTFOLIO_IDS[model_id],
        "hardware_profile_id": contract["hardware_target"]["profile_id"],
        "source_model": contract["model"]["path"],
        "operator_count": len(rows),
        "analog_operator_count": sum(row["placement"] == "analog_memory" for row in rows),
        "digital_support_operator_count": sum(row["placement"] == "digital_support" for row in rows),
        "memory_plan": plan["memory_plan"],
        "converter_plan": plan["converter_plan"],
        "comparison": {
            "metric": comparison["metric"],
            "relative_l2_output_difference": comparison["relative_l2_output_difference"],
            "pass": comparison["pass"],
            "proof_level": comparison["proof_level"],
        },
        "claim_boundary": contract["claim_boundary"],
        "source_plan": str((package / "hybrid_execution_plan.json").relative_to(ROOT)),
    }
    return entry, events


def main() -> int:
    hardware_profile = read(HARDWARE_PROFILE.parent, HARDWARE_PROFILE.name)
    models = []
    all_events = []
    for model_id, package in PACKAGES.items():
        entry, events = build_model_entry(model_id, package)
        models.append(entry)
        all_events.extend(events)
    for sequence, event in enumerate(all_events, 1):
        event["sequence"] = sequence
    package = {
        "schema_version": "aimc_hybrid_compiler_runtime_package.v1",
        "package_id": "hybrid_transformer_compiler_runtime_v1",
        "status": "package_generated_simulator_backed_physical_converter_blocked",
        "models": models,
        "shared_hardware": {
            "profile_id": hardware_profile["profile_id"],
            "profile_source": str(HARDWARE_PROFILE.relative_to(ROOT)),
            "analog_memory": "fixed-weight projection and MLP MatMul candidates",
            "digital_memory": "attention control, nonlinear, residual, calibration, fallback, and runtime control",
            "sram": "activations, partial sums, token state, KV-cache buffers, and fallback buffers",
            "shared_converter_gate": PHYSICAL_GATE,
        },
        "compiler_outputs": {
            "placement": "included per model",
            "bit_slicing": "included for deep MLP package; attention package inherits 8-bit simulator converter assumption",
            "runtime_schedule": "generated in hybrid_compiler_runtime_trace.json",
            "target_bytecode": "generated in target_bytecode.json by compile_hybrid_transformer_execution_package.py",
            "sram_allocator": "deterministic aligned per-workload offsets generated by the target compiler",
            "compiled_binary": "not_generated",
            "register_file": "not_generated",
        },
        "claim_boundary": {
            "allowed": "one shared compiler/runtime review package connects simulator-backed transformer and audio fixtures with explicit mixed-memory placement",
            "blocked": "compiled chip binary, measured board runtime, measured energy, calibrated silicon, pretrained-model accuracy, and production readiness",
        },
        "provenance": {"generated_at": datetime.now(timezone.utc).isoformat(), "not_measured_silicon": True},
    }
    trace = {
        "schema_version": "aimc_hybrid_compiler_runtime_trace.v1",
        "trace_id": "hybrid_transformer_compiler_runtime_trace_v1",
        "package_id": package["package_id"],
        "event_count": len(all_events),
        "events": all_events,
        "status": "operator_schedule_valid_target_bytecode_generated_hardware_binary_not_generated",
        "physical_converter_gate": PHYSICAL_GATE,
        "hardware_profile_id": hardware_profile["profile_id"],
        "claim_boundary": "operator-level schedule derived from simulator evidence; not a board runtime trace",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    report_lines = [
        "# Hybrid Transformer Compiler/Runtime Package",
        "",
        "This package is the shared handoff for tiny MLP, transformer MLP, attention, wake-word, normalized language-model serving, and imported edge-intake workloads.",
        "",
        f"- models: `{len(models)}`",
        f"- scheduled operators: `{sum(item['operator_count'] for item in models)}`",
        f"- schedule events: `{len(all_events)}`",
        "- target bytecode: `generated by the target compiler step`",
        "- hardware instruction-set binary: `not generated`",
        f"- physical converter gate: `{PHYSICAL_GATE}`",
        "",
        "The deep MLP and single-block packages assign fixed-weight MatMuls to analog memory and their nonlinear/residual operations to digital support. The attention package assigns static Q/K/V/output projections to analog candidates and keeps dynamic attention operations digital with SRAM buffers. The wake-word package retains dense layers as analog candidates but selects digital execution because converter overhead is not amortized at that workload size. The serving package keeps token lookup, attention control, KV-cache movement, and normalization digital while treating fixed projections as guarded analog candidates. The wearable and smart-camera packages are imported intake estimates and are explicitly not task or hardware results.",
        "",
        "Both model comparisons pass their named calibrated simulator fixture. The shared package does not upgrade those results to task, board, silicon, energy, or production evidence.",
        "",
        "## Next Compiler Gate",
        "",
        "The target compiler now emits aligned SRAM offsets, register writes, runtime commands, and a reproducible 64-bit review bytecode image for all 12 workload plans. The next compiler gate is an ISA-validated firmware image and observed runtime trace using a converter profile that matches the repaired physical topology.",
        "",
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "hybrid_compiler_runtime_package.json").write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "hybrid_compiler_runtime_trace.json").write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "hybrid_compiler_runtime_package.md").write_text("\n".join(report_lines), encoding="utf-8")
    print(f"package,{package['package_id']}")
    print(f"models,{len(models)}")
    print(f"operators,{sum(item['operator_count'] for item in models)}")
    print(f"events,{len(all_events)}")
    print("target_bytecode,generated_by_target_compiler")
    print("hardware_binary,not_generated")
    print(f"physical_converter_gate,{PHYSICAL_GATE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
