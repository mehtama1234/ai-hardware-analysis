#!/usr/bin/env python3
"""Run a bounded local sensitivity campaign for the multi-module GPT-2 slice."""

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
                                         capture_module_outputs,
                                         clear_projection, replace_forwards)
from tiled_projection_model import Profile, TiledProjection


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_scenario(model, tokenizer, modules, fixture, baseline, bounds, references,
                 selected, adc_bits, bound_multiplier, calibrated):
    bits_by_module = adc_bits if isinstance(adc_bits, dict) else {name: adc_bits for name in selected}
    projections = {
        name: TiledProjection(module.weight, module.bias, bounds[name] * bound_multiplier,
                              Profile(adc_bits=bits_by_module[name]), fixture["seed"])
        for name, module in modules.items() if name in selected
    }
    replacements = [(modules[name], lambda x, projection=projection: projection(x, ideal=False))
                    for name, projection in projections.items()]
    if calibrated:
        with replace_forwards(replacements):
            candidates = capture_module_outputs(model, tokenizer, modules, fixture["calibration"], "cpu")
        for name, projection in projections.items():
            scale, correction = affine_fit(references[name], candidates[name])
            projection.output_scale = scale
            projection.output_correction = correction
            clear_projection(projection)
    with replace_forwards(replacements):
        result = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
    quality = compare(baseline, result)
    return {
        "selected_modules": list(selected), "adc_bits": adc_bits,
        "activation_bound_multiplier": bound_multiplier, "calibrated": calibrated,
        "quality": quality,
        "screen_pass": quality["nll_increase_nats"] <= fixture["exploratory_screen"]["maximum_nll_increase_nats"]
        and quality["teacher_forced_argmax_agreement"] >= fixture["exploratory_screen"]["minimum_teacher_forced_argmax_agreement"],
        "module_error": {
            name: {
                "mean_trace_adc_clips": sum(row["adc_clipped_values"] for row in projection.trace),
                "mean_trace_dac_clips": sum(row["dac_clipped_values"] for row in projection.trace),
                "trace_events": len(projection.trace),
            } for name, projection in projections.items()
        },
    }


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
    references = capture_module_outputs(model, tokenizer, modules, fixture["calibration"], "cpu")
    baseline = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
    names = list(modules)
    scenarios = []
    for bits in (8, 10, 12, 14, 16):
        scenarios.append((names, bits, 1.0, True))
    for name in names:
        scenarios.append(([name], 12, 1.0, True))
    for count in (2, 3):
        scenarios.append((names[:count], 12, 1.0, True))
    # First governed mixed route: keep the weakest isolated module digital.
    scenarios.append(([names[0], names[2]], 12, 1.0, True))
    for multiplier in (0.75, 1.25):
        scenarios.append((names, 12, multiplier, True))
    scenarios.extend([
        (names, {names[0]: 12, names[1]: 16, names[2]: 12}, 1.0, True),
        (names, {names[0]: 16, names[1]: 12, names[2]: 12}, 1.0, True),
        (names, {names[0]: 12, names[1]: 12, names[2]: 16}, 1.0, True),
        (names, {names[0]: 14, names[1]: 16, names[2]: 14}, 1.0, True),
    ])
    results = []
    for index, scenario in enumerate(scenarios):
        print(f"scenario {index + 1}/{len(scenarios)}", flush=True)
        results.append(run_scenario(model, tokenizer, modules, fixture, baseline, bounds, references, *scenario))
    passing = [row for row in results if row["screen_pass"]]
    report = {
        "schema_version": "gpt2-multimodule-sensitivity-v0.1",
        "result_type": "local_multi_module_quality_sensitivity_campaign",
        "source": {"fixture": {"path": str(args.fixture), "sha256": digest(args.fixture)},
                   "runner": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}},
        "model_revision": fixture["revision"], "target_modules": names,
        "calibration_split": fixture["calibration"], "evaluation_split": fixture["evaluation"],
        "activation_bounds": bounds, "scenario_count": len(results), "results": results,
        "summary": {"passing_screen_scenarios": len(passing),
                    "best_argmax_agreement": max(row["quality"]["teacher_forced_argmax_agreement"] for row in results),
                    "best_scenario": max(results, key=lambda row: (row["quality"]["teacher_forced_argmax_agreement"], -row["quality"]["nll_increase_nats"])),
                    "interpretation": "No scenario authorizes analog execution; passing scenarios, if any, are local numerical sensitivity evidence only."},
        "claim_boundary": "Local CPU sensitivity replay of a pinned pretrained-model slice; no measured hardware latency, energy, silicon yield, or analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "sensitivity_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    manifest = {"files": [{"path": str(report_path), "sha256": digest(report_path)},
                          {"path": str(args.fixture), "sha256": digest(args.fixture)},
                          {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}]}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "scenarios": len(results), "passing": len(passing)}, sort_keys=True))


if __name__ == "__main__":
    main()
