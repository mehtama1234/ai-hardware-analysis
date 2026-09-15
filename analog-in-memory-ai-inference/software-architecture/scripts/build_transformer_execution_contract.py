#!/usr/bin/env python3
"""Build the first machine-readable transformer-to-chip execution package.

This is intentionally a planning/evidence artifact, not a performance claim.
It reuses the existing ONNX analyzer and hardware-placement policy, then makes
movement, conversion, fallback, and claim boundaries explicit for a selected
workload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from hardware_placement import build_hardware_placement  # noqa: E402
from onnx_analyzer import analyze_model  # noqa: E402


SCHEMA_VERSION = "transformer-execution-contract-v0.1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def shape_volume(shape: str | None) -> int:
    if not shape or not shape.startswith("[") or not shape.endswith("]"):
        return 0
    volume = 1
    found = False
    for value in shape[1:-1].split(","):
        value = value.strip()
        if value.isdigit():
            volume *= int(value)
            found = True
    return volume if found else 0


def placement_rows(analysis: dict[str, Any], placement: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = {row["operator_id"]: row for row in placement["placement_rows"]}
    for layer in analysis["layers"]:
        rows.setdefault(layer["id"], {})
    return rows


def effective_placement(layer: dict[str, Any], phase: str, physical_analog_allowed: bool | None = None) -> tuple[str, str]:
    """Apply the first attention policy on top of generic operator mapping."""
    operator_id = str(layer.get("id", "")).lower()
    operator = layer.get("operator")
    if "attention" in operator_id or operator_id.startswith("attn."):
        if "score" in operator_id or "value" in operator_id or operator in {"Softmax", "Div"}:
            return "digital", "dynamic attention state stays digital in the first decode slice"
        if phase == "decode" and operator == "MatMul" and "out" not in operator_id and not any(
            token in operator_id for token in ("q", "k", "v")
        ):
            return "digital", "unclassified decode MatMul stays digital until cache sensitivity is measured"
        if operator == "MatMul":
            if physical_analog_allowed is False:
                return "digital_fallback", "physical converter gate is not accepted; analog claim is disabled"
            return "analog_candidate", "fixed projection may be analog after token-level sensitivity and physical gates"
    placement = layer.get("placement", "digital")
    if placement == "analog" and physical_analog_allowed is False:
        return "digital_fallback", "physical converter gate is not accepted; analog claim is disabled"
    return placement, layer.get("reason", "existing hardware policy")


def build_contract(
    model_path: Path,
    target_profile: str,
    calibration_profile: str,
    phase: str,
    physical_gate: dict[str, Any] | None = None,
    enforce_physical_gate: bool = False,
) -> dict[str, Any]:
    analysis = analyze_model(model_path, target_profile=target_profile, calibration_profile=calibration_profile)
    placement = build_hardware_placement(analysis)
    target = {
        "name": analysis["target"],
        "profile_id": target_profile,
        "latency_target_ms": analysis["targets"]["latency"],
        "energy_target": analysis["targets"]["energy"],
        "accuracy_target": analysis["targets"]["accuracy"],
    }
    rows = placement_rows(analysis, placement)
    layers = []
    movement = []
    schedule = []
    has_attention = any(
        "attention" in str(layer.get("id", "")).lower()
        or str(layer.get("id", "")).lower().startswith("attn.")
        for layer in analysis["layers"]
    )
    physical_analog_allowed = None
    if enforce_physical_gate and physical_gate is not None:
        physical_analog_allowed = bool(physical_gate.get("analog_allowed_for_physical_claim", False))
    previous_execution = "digital"
    for index, layer in enumerate(analysis["layers"]):
        row = rows[layer["id"]]
        volume = shape_volume(layer.get("shape"))
        placement_name, placement_reason = effective_placement(layer, phase, physical_analog_allowed)
        if placement_name in {"unsupported", "fallback", "analog_candidate", "digital_fallback"}:
            execution = "analog" if placement_name == "analog_candidate" else "digital_fallback"
        elif placement_name == "analog":
            execution = "analog"
        else:
            execution = "digital"
        if execution == "digital_fallback":
            execution = "digital_fallback"
        analog = execution == "analog"
        input_bytes = volume if volume else None
        output_bytes = volume if volume else None
        conversion_events = []
        if previous_execution != "analog" and analog:
            conversion_events.append("DAC")
        if previous_execution == "analog" and not analog:
            conversion_events.append("ADC")
        boundary = layer.get("boundaries", "")
        if conversion_events:
            boundary = ", ".join(conversion_events) + " boundary"
        if "DAC" in boundary and "DAC" not in conversion_events:
            conversion_events.append("DAC")
        if "ADC" in boundary and "ADC" not in conversion_events:
            conversion_events.append("ADC")
        layers.append(
            {
                "operator_id": layer["id"],
                "operator": layer["operator"],
                "shape": layer.get("shape"),
                "fixed_weight_candidate": layer["operator"] in {"MatMul", "Gemm", "Conv"},
                "placement": execution,
                "placement_reason": placement_reason,
                "sensitivity_class": row.get("model_sensitivity_class"),
                "expected_error_source": row.get("expected_error_source"),
                "fallback": {
                    "allowed": execution != "analog" or row.get("governor_fields", {}).get("allow_analog") is not True,
                    "action": "digital_fallback",
                    "reason": row.get("fallback_point"),
                },
            }
        )
        movement.append(
            {
                "operator_id": layer["id"],
                "input_bytes_int8_estimate": input_bytes,
                "output_bytes_int8_estimate": output_bytes,
                "memory_energy_uj_estimate": layer.get("memory_energy_uj"),
                "conversion_events": conversion_events,
                "conversion_energy_uj_estimate": layer.get("conversion_energy_uj"),
                "boundary": boundary,
                "kv_cache": (
                    "digital KV-cache state is required for attention/decode"
                    if has_attention and phase == "decode"
                    else "not present in this MLP fixture; required in attention/decode follow-on"
                ),
                "status": "estimated_from_shape_and_target_profile",
            }
        )
        schedule.append(
            {
                "event_id": f"event.{index + 1:03d}",
                "operator_id": layer["id"],
                "execution": execution,
                "tile": "analog_tile_0" if analog else "digital_support",
                "memory": "analog_array_and_sram" if analog else "sram_and_digital",
                "precision": "target_profile_default",
                "conversion_events": conversion_events,
                "calibration_profile": calibration_profile if analog else None,
                "fallback_action": "digital_fallback" if analog else None,
                "estimated_latency_ms": layer.get("latency_ms"),
                "estimated_energy_uj": layer.get("energy_uj"),
            }
        )
        previous_execution = execution
    state_rows = []
    state_schedule = []
    if has_attention and phase == "decode":
        state_rows = [
            {
                "operator_id": "kv_cache.read",
                "kind": "stateful_memory",
                "placement": "digital_memory",
                "bytes_per_token_estimate": "sequence_length * heads * head_dimension * bytes_per_element",
                "reason": "decode reads prior keys and values generated at runtime",
            },
            {
                "operator_id": "kv_cache.write",
                "kind": "stateful_memory",
                "placement": "digital_memory",
                "bytes_per_token_estimate": "heads * head_dimension * bytes_per_element",
                "reason": "decode appends the current token state",
            },
        ]
        state_schedule = [
            {
                "event_id": "state.kv_cache.read",
                "operator_id": "kv_cache.read",
                "execution": "digital_memory",
                "memory": "kv_cache",
                "fallback_action": None,
            },
            {
                "event_id": "state.kv_cache.write",
                "operator_id": "kv_cache.write",
                "execution": "digital_memory",
                "memory": "kv_cache",
                "fallback_action": None,
            },
        ]
    return {
        "schema_version": SCHEMA_VERSION,
        "workload_contract": {
            "workload_id": f"{model_path.stem}_{phase}_v1",
            "model_file": model_path.name,
            "model_sha256": sha256(model_path),
            "phase": phase,
            "batch_size": 1,
            "sequence_length": "fixture-defined; decode contract required before LLM claim",
            "quality_metric": "relative_output_residual_then_token_agreement",
            "latency_metric": "time_per_token",
            "energy_metric": "joules_per_token",
            "fallback_policy": "digital_fallback_on_physical_or_quality_gate_failure",
            "target": target,
            "calibration_profile": calibration_profile,
            "physical_gate": physical_gate or {
                "status": "not_imported",
                "analog_allowed_for_physical_claim": False,
                "reason": "converter PVT, mismatch, extracted-layout, and board evidence are separate gates",
            },
            "kv_cache": {
                "status": "required_for_decode",
                "initial_policy": "digital_memory",
                "state_operations": [item["operator_id"] for item in state_rows],
            },
        },
        "operator_inventory": {
            "operators": layers,
            "state_operations": state_rows,
            "summary": placement["summary"],
        },
        "movement_ledger": {
            "denominator": "one fixture execution; token-level decode ledger is a required follow-on",
            "rows": movement + state_rows,
            "boundary_events": analysis.get("boundary_events", []),
            "energy_breakdown": analysis.get("energy_breakdown", []),
        },
        "hybrid_execution_plan": {
            "schedule": schedule + state_schedule,
            "memory_policy": "keep activations, partial sums, calibration values, and fallback buffers in SRAM/digital support",
            "attention_policy": "not represented by this MLP fixture; keep scores, Softmax, and KV-cache digital in the next slice",
        },
        "claim_boundary": {
            "allowed": "This package is a reproducible ONNX-derived planning and estimated movement artifact for the named fixture.",
            "refused": "It is not measured board latency, measured energy, calibrated silicon, full LLM decode, or production readiness.",
            "next_gate": "Replace the synthetic output replay with measured per-tile calibration, then run held-out token-level attention/decode agreement; physical enforcement status is recorded in the workload contract.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=ROOT / "samples" / "deep-transformer-mlp-stack.onnx")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-profile", default="robotics", choices=["wearable", "camera", "robotics"])
    parser.add_argument("--calibration-profile", default="sim-wearable-v0")
    parser.add_argument("--phase", default="prefill", choices=["prefill", "decode"])
    parser.add_argument("--physical-gate", type=Path, help="EDA physical-evidence gate JSON")
    parser.add_argument("--enforce-physical-gate", action="store_true", help="force analog candidates to fallback when the imported gate is not accepted")
    args = parser.parse_args()
    if not args.model.exists():
        raise SystemExit(f"model not found: {args.model}")
    args.output.mkdir(parents=True, exist_ok=True)
    physical_gate = None
    if args.physical_gate:
        if not args.physical_gate.exists():
            raise SystemExit(f"physical gate not found: {args.physical_gate}")
        physical_gate = json.loads(args.physical_gate.read_text(encoding="utf-8"))
        if "analog_allowed_for_physical_claim" not in physical_gate:
            physical_gate["analog_allowed_for_physical_claim"] = bool(
                physical_gate.get("ready_for_candidate_post_layout_payload", False)
            )
        physical_gate["source_path"] = str(args.physical_gate)
        physical_gate["imported_for_claim"] = True
    package = build_contract(
        args.model,
        args.target_profile,
        args.calibration_profile,
        args.phase,
        physical_gate=physical_gate,
        enforce_physical_gate=args.enforce_physical_gate,
    )
    for name, payload in package.items():
        (args.output / f"{name}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "files": sorted(path.name for path in args.output.glob("*.json")),
        "model": str(args.model),
        "model_sha256": sha256(args.model),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
