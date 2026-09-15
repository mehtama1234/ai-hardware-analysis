#!/usr/bin/env python3
"""Validate governed multi-module routes on a fresh disjoint text set."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_gpt2_hybrid_evaluation import compare, evaluate
from run_gpt2_multimodule_replay import (PINNED_REVISION, affine_fit,
                                         capture_activation_bounds,
                                         capture_module_outputs, clear_projection,
                                         replace_forwards)
from tiled_projection_model import Profile, TiledProjection


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-path", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--calibration-fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--weight-bits", type=int, default=8)
    parser.add_argument("--dac-bits", type=int, default=10)
    parser.add_argument("--adc-bits", type=int, default=12)
    parser.add_argument("--bound-multiplier", type=float, default=1.0)
    parser.add_argument("--range-multipliers", type=str, default=None,
                        help="comma-separated per-module range multipliers")
    args = parser.parse_args()
    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    calibration_fixture = json.loads(args.calibration_fixture.read_text(encoding="utf-8"))
    if fixture["revision"] != PINNED_REVISION or calibration_fixture["revision"] != PINNED_REVISION:
        raise SystemExit("stress and calibration fixtures must use the pinned revision")
    if set(fixture["evaluation"]) & (set(fixture["calibration"]) | set(calibration_fixture["calibration"])):
        raise SystemExit("stress evaluation overlaps an existing split")
    torch.set_num_threads(args.threads)
    model = AutoModelForCausalLM.from_pretrained(args.snapshot_path, local_files_only=True,
                                                 use_safetensors=True, attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(args.snapshot_path, local_files_only=True)
    modules = {name: model.get_submodule(name) for name in fixture["target_modules"]}
    names = list(modules)
    range_multipliers = ([float(value) for value in args.range_multipliers.split(",")]
                         if args.range_multipliers else [args.bound_multiplier] * len(names))
    if len(range_multipliers) != len(names) or any(value <= 0 for value in range_multipliers):
        raise SystemExit("range multipliers must contain one positive value per module")
    bounds = capture_activation_bounds(model, tokenizer, modules, calibration_fixture["calibration"], "cpu")
    reference_calibration = capture_module_outputs(model, tokenizer, modules, calibration_fixture["calibration"], "cpu")
    baseline = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
    routes = {
        "c_fc_only": [names[0]], "c_proj_only": [names[1]], "attn_only": [names[2]],
        "c_attn_recommended": [names[2]], "full_three_module": names,
    }
    # Keep one explicit repeated recommendation label and one candidate full route;
    # the duplicate is intentionally omitted from the output route set below.
    routes.pop("c_attn_recommended")
    results = {}
    for route, selected in routes.items():
        projections = {name: TiledProjection(modules[name].weight, modules[name].bias, bounds[name] * range_multipliers[names.index(name)],
                                              Profile(weight_bits=args.weight_bits, dac_bits=args.dac_bits,
                                                      adc_bits=args.adc_bits), fixture["seed"])
                       for name in selected}
        replacements = [(modules[name], lambda x, projection=projection: projection(x, ideal=False))
                        for name, projection in projections.items()]
        # Capture the calibration candidate through the replacements explicitly.
        with replace_forwards(replacements):
            calibration_candidate = capture_module_outputs(model, tokenizer, modules,
                                                            calibration_fixture["calibration"], "cpu")
        for name, projection in projections.items():
            scale, correction = affine_fit(reference_calibration[name], calibration_candidate[name])
            projection.output_scale = scale
            projection.output_correction = correction
            clear_projection(projection)
        with replace_forwards(replacements):
            candidate = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
        quality = compare(baseline, candidate)
        results[route] = {
            "analog_modules": selected,
            "digital_modules": [name for name in names if name not in selected],
            "quality": quality,
            "screen_pass": quality["nll_increase_nats"] <= fixture["exploratory_screen"]["maximum_nll_increase_nats"]
            and quality["teacher_forced_argmax_agreement"] >= fixture["exploratory_screen"]["minimum_teacher_forced_argmax_agreement"],
        }
    recommended = results["attn_only"]
    decision = ("numerical_recommendation_generalizes_but_hardware_authorization_remains_closed"
                if all(row["screen_pass"] for row in results.values())
                else "numerical_recommendation_does_not_generalize_and_hardware_authorization_remains_closed")
    report = {
        "schema_version": "gpt2-multimodule-governor-stress-v0.1",
        "result_type": "local_governor_disjoint_stress_validation",
        "sources": {"stress_fixture": {"path": str(args.fixture), "sha256": digest(args.fixture)},
                    "calibration_fixture": {"path": str(args.calibration_fixture), "sha256": digest(args.calibration_fixture)},
                    "runner": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}},
        "model_revision": fixture["revision"], "target_modules": names,
        "calibration_split": calibration_fixture["calibration"], "evaluation_split": fixture["evaluation"],
        "profile": {"weight_bits": args.weight_bits, "dac_bits": args.dac_bits, "adc_bits": args.adc_bits,
                    "bound_multiplier": args.bound_multiplier, "range_multipliers": range_multipliers},
        "results": results,
        "recommended_route": {"route": "attn_only", "screen_pass": recommended["screen_pass"],
                              "quality": recommended["quality"]},
        "decision": decision,
        "analog_authorized": False,
        "claim_boundary": "Local CPU disjoint stress validation only; no hardware latency, energy, silicon yield, or analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "stress_validation_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        {"path": str(args.fixture), "sha256": digest(args.fixture)},
        {"path": str(args.calibration_fixture), "sha256": digest(args.calibration_fixture)},
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "routes": len(results),
                      "recommended_pass": recommended["screen_pass"]}, sort_keys=True))


if __name__ == "__main__":
    main()
