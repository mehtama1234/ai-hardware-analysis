#!/usr/bin/env python3
"""Bind a measured SAR qualification profile to one frozen GPT-2 projection.

This is a planning and provenance artifact. It deliberately refuses to turn a
schematic converter result into an analog placement authorization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--sar-profile", type=Path, required=True)
    parser.add_argument("--remap-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    evaluation: dict[str, Any] = json.loads(args.evaluation.read_text())
    profile: dict[str, Any] = json.loads(args.sar_profile.read_text())
    remap: dict[str, Any] = json.loads(args.remap_contract.read_text())
    variants = evaluation.get("variants", [])
    selected = next((v for v in variants if v.get("id") == "dac10_weight8_adc12"), None)
    if selected is None:
        raise SystemExit("evaluation must contain the dac10_weight8_adc12 variant")
    contract = selected.get("contract", {})
    per_vector = contract.get("per_vector", {})
    required = ("macs", "dac_conversions_without_column_tile_broadcast",
                "adc_conversions_after_differential_subtraction", "array_evaluations",
                "digital_partial_sum_additions")
    missing = [key for key in required if key not in per_vector]
    if missing:
        raise SystemExit(f"selected variant is missing schedule fields: {missing}")

    supported = len(profile.get("supported_cases", []))
    open_cases = len(profile.get("open_cases", []))
    remap_usable = int(remap.get("calibration_policy", {}).get("usable_case_count", 0))
    placement_allowed = bool(
        evaluation.get("placement", {}).get("authorized_analog_modules")
        and profile.get("authorization", {}).get("analog_authorized")
        and remap_usable > 0 and open_cases == 0
    )
    result = {
        "schema_version": "profile-driven-transformer-contract-v0.1",
        "result_type": "guarded_gpt2_projection_schedule",
        "sources": {
            "evaluation": {"path": str(args.evaluation), "sha256": sha256(args.evaluation)},
            "sar_profile": {"path": str(args.sar_profile), "sha256": sha256(args.sar_profile)},
            "remap_contract": {"path": str(args.remap_contract), "sha256": sha256(args.remap_contract)},
        },
        "model_binding": {
            "model_id": evaluation.get("model", {}).get("id"),
            "revision": evaluation.get("model", {}).get("revision"),
            "target_module": evaluation.get("model", {}).get("target_module"),
            "projection_shape": contract.get("weight_shape_input_output"),
        },
        "selected_numerical_variant": {
            "id": selected["id"],
            "quality": selected.get("quality", {}),
            "status": "numerical_control_only",
        },
        "per_vector_schedule": per_vector,
        "converter_qualification_binding": {
            "supported_profile_cases": supported,
            "open_profile_cases": open_cases,
            "remap_usable_cases": remap_usable,
            "profile_calibrated": False,
            "analog_placement_allowed": placement_allowed,
        },
        "execution_policy": {
            "authoritative_path": "native_digital_fallback",
            "analog_candidate": evaluation.get("model", {}).get("target_module"),
            "fallback_required": True,
            "fallback_trigger": ["unqualified_corner", "code_collision", "out_of_set_code",
                                  "ADC_clip", "timing_timeout", "held_out_quality_failure"],
            "digital_always_required": ["attention", "KV_cache", "normalization", "scheduler",
                                         "partial_accumulation", "conversion_control"],
        },
        "next_experiment": {
            "name": "held_out_profile_driven_gpt2_projection",
            "calibration_split": "circuit references used only to fit per-converter remap",
            "validation_split": "new circuit references and mismatch seeds",
            "workload_split": "frozen GPT-2 evaluation contexts not used for calibration",
            "required_outputs": ["baseline logits and tokens", "profile-driven logits and tokens",
                                  "conversion_count", "fallback_count", "bytes_moved",
                                  "latency_scope", "energy_coefficients_or_missingness"],
        },
        "decision": "retain_native_digital_execution_until_held_out_profile_validation_passes",
        "claim_boundary": "This contract binds measured schematic SAR metadata to a real GPT-2 projection schedule. It does not claim analog placement, silicon yield, latency, energy advantage, or hardware acceleration.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"output": str(args.output), "analog_placement_allowed": placement_allowed,
                      "supported_profile_cases": supported, "open_profile_cases": open_cases,
                      "remap_usable_cases": remap_usable}))


if __name__ == "__main__":
    main()
