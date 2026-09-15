#!/usr/bin/env python3
"""Decompose multi-module quality loss into numerical error-budget components."""

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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-path", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    if fixture["revision"] != PINNED_REVISION:
        raise SystemExit("fixture revision is not pinned")
    torch.set_num_threads(args.threads)
    torch.manual_seed(fixture["seed"])
    model = AutoModelForCausalLM.from_pretrained(args.snapshot_path, local_files_only=True,
                                                 use_safetensors=True, attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(args.snapshot_path, local_files_only=True)
    modules = {name: model.get_submodule(name) for name in fixture["target_modules"]}
    bounds = capture_activation_bounds(model, tokenizer, modules, fixture["calibration"], "cpu")
    calibration_reference = capture_module_outputs(model, tokenizer, modules, fixture["calibration"], "cpu")
    baseline = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
    configurations = {
        "ideal_control": None,
        "weight_quantization_only": {"weight_bits": 8, "dac_bits": 16, "adc_bits": 16},
        "dac_quantization_only": {"weight_bits": 16, "dac_bits": 10, "adc_bits": 16},
        "adc_quantization_only": {"weight_bits": 16, "dac_bits": 16, "adc_bits": 12},
        "combined_current_profile": {"weight_bits": 8, "dac_bits": 10, "adc_bits": 12},
    }
    results = {}
    for label, config in configurations.items():
        if config is None:
            results[label] = {
                "profile": "ideal",
                "quality": {"screen_pass": True, "teacher_forced_argmax_agreement": 1.0,
                            "nll_increase_nats": 0.0, "generation_exact_match_count": len(fixture["evaluation"])},
                "module_error": {}, "claim_boundary": "Local ideal software control only.",
            }
            continue
        profile = Profile(**config)
        projections = {name: TiledProjection(module.weight, module.bias, bounds[name], profile, fixture["seed"])
                       for name, module in modules.items()}
        replacements = [(modules[name], lambda x, projection=projection: projection(x, ideal=False))
                        for name, projection in projections.items()]
        with replace_forwards(replacements):
            calibration_candidate = capture_module_outputs(model, tokenizer, modules, fixture["calibration"], "cpu")
        calibration = {}
        for name, projection in projections.items():
            scale, correction = affine_fit(calibration_reference[name], calibration_candidate[name])
            projection.output_scale = scale
            projection.output_correction = correction
            before = calibration_candidate[name].double() - calibration_reference[name].double()
            after = calibration_candidate[name].double() * scale.double() + correction.double() - calibration_reference[name].double()
            calibration[name] = {
                "relative_l2_before": float(torch.linalg.vector_norm(before) /
                                             torch.linalg.vector_norm(calibration_reference[name].double()).clamp_min(1e-12)),
                "relative_l2_after": float(torch.linalg.vector_norm(after) /
                                            torch.linalg.vector_norm(calibration_reference[name].double()).clamp_min(1e-12)),
            }
            clear_projection(projection)
        with replace_forwards(replacements):
            candidate = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
        quality = compare(baseline, candidate)
        quality["screen_pass"] = (quality["nll_increase_nats"] <= fixture["exploratory_screen"]["maximum_nll_increase_nats"]
                                   and quality["teacher_forced_argmax_agreement"] >= fixture["exploratory_screen"]["minimum_teacher_forced_argmax_agreement"])
        results[label] = {
            "profile": config, "quality": quality, "calibration": calibration,
            "module_error": {name: {
                "output_relative_l2": calibration[name]["relative_l2_after"],
                "adc_clipped_values": sum(row["adc_clipped_values"] for row in projection.trace),
                "dac_clipped_values": sum(row["dac_clipped_values"] for row in projection.trace),
            } for name, projection in projections.items()},
            "claim_boundary": "Local calibrated CPU error-budget replay; no physical hardware claim.",
        }
    report = {
        "schema_version": "gpt2-multimodule-error-budget-v0.1",
        "result_type": "local_multi_module_numerical_error_budget",
        "sources": {"fixture": {"path": str(args.fixture), "sha256": digest(args.fixture)},
                    "runner": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}},
        "model_revision": fixture["revision"], "target_modules": fixture["target_modules"],
        "calibration_split": fixture["calibration"], "evaluation_split": fixture["evaluation"],
        "configurations": results,
        "interpretation": "A component passes only when the same joint three-module workload clears both quality thresholds; component isolation does not establish hardware causality.",
        "analog_authorized": False,
        "claim_boundary": "Local CPU numerical error budget only; no measured hardware latency, energy, silicon yield, or analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "error_budget_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        {"path": str(args.fixture), "sha256": digest(args.fixture)},
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "configurations": len(results),
                      "passing_components": sum(row["quality"]["screen_pass"] for row in results.values())}, sort_keys=True))


if __name__ == "__main__":
    main()
