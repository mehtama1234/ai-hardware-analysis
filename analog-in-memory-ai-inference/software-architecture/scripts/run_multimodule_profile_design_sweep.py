#!/usr/bin/env python3
"""Sweep redesigned numerical converter profiles on the fixed multi-module workload."""

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
    references = capture_module_outputs(model, tokenizer, modules, fixture["calibration"], "cpu")
    baseline = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
    designs = [
        ("current_profile", 8, 10, 12, 1.0),
        ("adc14", 8, 10, 14, 1.0),
        ("adc16", 8, 10, 16, 1.0),
        ("dac14_adc12", 8, 14, 12, 1.0),
        ("dac16_adc12", 8, 16, 12, 1.0),
        ("weight16_dac16_adc14", 16, 16, 14, 1.0),
        ("adc12_range025", 8, 10, 12, 0.25),
        ("adc12_range050", 8, 10, 12, 0.50),
        ("adc12_range075", 8, 10, 12, 0.75),
        ("adc12_range125", 8, 10, 12, 1.25),
        ("all16", 16, 16, 16, 1.0),
    ]
    results = {}
    screen = fixture["exploratory_screen"]
    for label, weight_bits, dac_bits, adc_bits, range_multiplier in designs:
        profile = Profile(weight_bits=weight_bits, dac_bits=dac_bits, adc_bits=adc_bits)
        projections = {name: TiledProjection(module.weight, module.bias, bounds[name] * range_multiplier,
                                              profile, fixture["seed"])
                       for name, module in modules.items()}
        replacements = [(modules[name], lambda x, projection=projection: projection(x, ideal=False))
                        for name, projection in projections.items()]
        with replace_forwards(replacements):
            calibrated = capture_module_outputs(model, tokenizer, modules, fixture["calibration"], "cpu")
        calibration = {}
        for name, projection in projections.items():
            gain, offset = affine_fit(references[name], calibrated[name])
            projection.output_scale, projection.output_correction = gain, offset
            before = calibrated[name].double() - references[name].double()
            after = calibrated[name].double() * gain.double() + offset.double() - references[name].double()
            calibration[name] = {
                "relative_l2_before": float(torch.linalg.vector_norm(before) / torch.linalg.vector_norm(references[name].double()).clamp_min(1e-12)),
                "relative_l2_after": float(torch.linalg.vector_norm(after) / torch.linalg.vector_norm(references[name].double()).clamp_min(1e-12)),
            }
            clear_projection(projection)
        with replace_forwards(replacements):
            candidate = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
        quality = compare(baseline, candidate)
        quality["screen_pass"] = (quality["nll_increase_nats"] <= screen["maximum_nll_increase_nats"]
                                   and quality["teacher_forced_argmax_agreement"] >= screen["minimum_teacher_forced_argmax_agreement"])
        results[label] = {
            "profile": {"weight_bits": weight_bits, "dac_bits": dac_bits, "adc_bits": adc_bits,
                        "activation_bound_multiplier": range_multiplier, "calibrated": True},
            "quality": quality, "calibration": calibration,
            "total_adc_clipped_values": sum(sum(row["adc_clipped_values"] for row in projection.trace) for projection in projections.values()),
            "total_dac_clipped_values": sum(sum(row["dac_clipped_values"] for row in projection.trace) for projection in projections.values()),
        }
    report = {
        "schema_version": "gpt2-multimodule-profile-design-sweep-v0.1",
        "result_type": "local_multi_module_converter_profile_design_sweep",
        "source": {"fixture": {"path": str(args.fixture), "sha256": digest(args.fixture)},
                   "runner": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}},
        "model_revision": fixture["revision"], "target_modules": fixture["target_modules"],
        "calibration_split": fixture["calibration"], "evaluation_split": fixture["evaluation"],
        "design_count": len(results), "designs": results,
        "passing_designs": [name for name, row in results.items() if row["quality"]["screen_pass"]],
        "analog_authorized": False,
        "claim_boundary": "Local calibrated CPU converter-profile sweep only; no measured hardware latency, energy, silicon yield, or analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "profile_design_sweep_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        {"path": str(args.fixture), "sha256": digest(args.fixture)},
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "designs": len(results),
                      "passing_designs": report["passing_designs"]}, sort_keys=True))


if __name__ == "__main__":
    main()
