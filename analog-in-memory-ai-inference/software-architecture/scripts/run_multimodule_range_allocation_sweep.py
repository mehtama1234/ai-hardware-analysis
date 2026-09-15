#!/usr/bin/env python3
"""Test module-specific activation ranges with a fixed high-fidelity profile."""

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
    model = AutoModelForCausalLM.from_pretrained(args.snapshot_path, local_files_only=True,
                                                 use_safetensors=True, attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(args.snapshot_path, local_files_only=True)
    modules = {name: model.get_submodule(name) for name in fixture["target_modules"]}
    names = list(modules)
    bounds = capture_activation_bounds(model, tokenizer, modules, fixture["calibration"], "cpu")
    references = capture_module_outputs(model, tokenizer, modules, fixture["calibration"], "cpu")
    baseline = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
    designs = {
        "uniform_1": {name: 1.0 for name in names},
        "fc_075": {names[0]: 0.75, names[1]: 1.0, names[2]: 1.0},
        "proj_075": {names[0]: 1.0, names[1]: 0.75, names[2]: 1.0},
        "attn_075": {names[0]: 1.0, names[1]: 1.0, names[2]: 0.75},
        "fc_125": {names[0]: 1.25, names[1]: 1.0, names[2]: 1.0},
        "proj_125": {names[0]: 1.0, names[1]: 1.25, names[2]: 1.0},
        "attn_125": {names[0]: 1.0, names[1]: 1.0, names[2]: 1.25},
        "fc_attn_075": {names[0]: 0.75, names[1]: 1.0, names[2]: 0.75},
    }
    screen = fixture["exploratory_screen"]
    results = {}
    for label, allocation in designs.items():
        profile = Profile(weight_bits=16, dac_bits=16, adc_bits=14)
        projections = {name: TiledProjection(modules[name].weight, modules[name].bias,
                                              bounds[name] * allocation[name], profile, fixture["seed"])
                       for name in names}
        replacements = [(modules[name], lambda x, projection=projection: projection(x, ideal=False))
                        for name, projection in projections.items()]
        with replace_forwards(replacements):
            calibrated = capture_module_outputs(model, tokenizer, modules, fixture["calibration"], "cpu")
        for name, projection in projections.items():
            gain, offset = affine_fit(references[name], calibrated[name])
            projection.output_scale, projection.output_correction = gain, offset
            clear_projection(projection)
        with replace_forwards(replacements):
            candidate = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
        quality = compare(baseline, candidate)
        quality["screen_pass"] = (quality["nll_increase_nats"] <= screen["maximum_nll_increase_nats"]
                                   and quality["teacher_forced_argmax_agreement"] >= screen["minimum_teacher_forced_argmax_agreement"])
        results[label] = {
            "range_multipliers": allocation,
            "profile": {"weight_bits": 16, "dac_bits": 16, "adc_bits": 14},
            "quality": quality,
            "total_dac_clipped_values": sum(sum(row["dac_clipped_values"] for row in projection.trace) for projection in projections.values()),
            "total_adc_clipped_values": sum(sum(row["adc_clipped_values"] for row in projection.trace) for projection in projections.values()),
        }
    report = {
        "schema_version": "gpt2-multimodule-range-allocation-v0.1",
        "result_type": "local_module_specific_activation_range_sweep",
        "sources": {"fixture": {"path": str(args.fixture), "sha256": digest(args.fixture)},
                    "runner": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}},
        "model_revision": fixture["revision"], "target_modules": names,
        "calibration_split": fixture["calibration"], "evaluation_split": fixture["evaluation"],
        "design_count": len(results), "designs": results,
        "passing_designs": [name for name, row in results.items() if row["quality"]["screen_pass"]],
        "analog_authorized": False,
        "claim_boundary": "Local calibrated CPU module-specific range sweep only; no measured hardware latency, energy, silicon yield, or analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "range_allocation_report.json"
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
