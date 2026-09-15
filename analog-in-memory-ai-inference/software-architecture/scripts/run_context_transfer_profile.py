#!/usr/bin/env python3
"""Compare global and magnitude-context affine transfer calibration."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_gpt2_hybrid_evaluation import compare, evaluate
from run_gpt2_multimodule_replay import (PINNED_REVISION,
                                         capture_activation_bounds,
                                         capture_module_outputs, clear_projection,
                                         replace_forwards)
from tiled_projection_model import Profile, TiledProjection


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit_affine(reference, candidate):
    reference = reference.double()
    candidate = candidate.double()
    reference_mean = reference.mean(dim=0)
    candidate_mean = candidate.mean(dim=0)
    centered_reference = reference - reference_mean
    centered_candidate = candidate - candidate_mean
    variance = (centered_candidate * centered_candidate).sum(dim=0).clamp_min(1e-12)
    scale = (centered_candidate * centered_reference).sum(dim=0) / variance
    correction = reference_mean - scale * candidate_mean
    return scale.float(), correction.float()


def capture_input_energy(model, tokenizer, modules, texts):
    values = {name: [] for name in modules}
    handles = []
    for name, module in modules.items():
        def observe(_module, inputs, module_name=name):
            values[module_name].append(inputs[0].detach().reshape(-1, inputs[0].shape[-1]).norm(dim=1).cpu())
        handles.append(module.register_forward_pre_hook(observe))
    try:
        with torch.inference_mode():
            for text in texts:
                model(**tokenizer(text, return_tensors="pt"), use_cache=False)
    finally:
        for handle in handles:
            handle.remove()
    return {name: torch.cat(parts) for name, parts in values.items()}


def fit_input_energy_residual(reference, candidate, energy):
    center = energy.median()
    centered_energy = (energy - center).to(candidate.dtype)
    ones = torch.ones_like(centered_energy)
    scales, corrections, residuals = [], [], []
    for index in range(candidate.shape[1]):
        design = torch.stack((candidate[:, index], ones, centered_energy), dim=1).double()
        coefficients = torch.linalg.lstsq(design, reference[:, index].double()).solution
        scales.append(coefficients[0])
        corrections.append(coefficients[1])
        residuals.append(coefficients[2])
    return torch.stack(scales).float(), torch.stack(corrections).float(), torch.stack(residuals).float(), center


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-path", type=Path, required=True)
    parser.add_argument("--calibration-fixture", type=Path, required=True)
    parser.add_argument("--original-fixture", type=Path, required=True)
    parser.add_argument("--stress-fixture", type=Path, required=True)
    parser.add_argument("--third-fixture", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    calibration_fixture = json.loads(args.calibration_fixture.read_text(encoding="utf-8"))
    original_fixture = json.loads(args.original_fixture.read_text(encoding="utf-8"))
    stress_fixture = json.loads(args.stress_fixture.read_text(encoding="utf-8"))
    third_fixture = json.loads(args.third_fixture.read_text(encoding="utf-8")) if args.third_fixture else None
    fixtures = (calibration_fixture, original_fixture, stress_fixture) + ((third_fixture,) if third_fixture else ())
    if any(fixture["revision"] != PINNED_REVISION for fixture in fixtures):
        raise SystemExit("all fixtures must use the pinned revision")
    evaluation_sets = [set(fixture["evaluation"]) for fixture in (original_fixture, stress_fixture) + ((third_fixture,) if third_fixture else ())]
    if set(calibration_fixture["calibration"]) & set.union(*evaluation_sets):
        raise SystemExit("calibration and evaluation splits overlap")
    if any(left & right for index, left in enumerate(evaluation_sets) for right in evaluation_sets[index + 1:]):
        raise SystemExit("evaluation splits overlap")
    torch.set_num_threads(args.threads)
    model = AutoModelForCausalLM.from_pretrained(args.snapshot_path, local_files_only=True,
                                                 use_safetensors=True, attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(args.snapshot_path, local_files_only=True)
    modules = {name: model.get_submodule(name) for name in calibration_fixture["target_modules"]}
    names = list(modules)
    bounds = capture_activation_bounds(model, tokenizer, modules, calibration_fixture["calibration"], "cpu")
    references = capture_module_outputs(model, tokenizer, modules, calibration_fixture["calibration"], "cpu")
    input_energies = capture_input_energy(model, tokenizer, modules, calibration_fixture["calibration"])
    datasets = {"original": original_fixture, "stress": stress_fixture}
    if third_fixture:
        datasets["third_holdout"] = third_fixture
    baselines = {label: evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
                 for label, fixture in datasets.items()}
    results = {}
    for mode in ("global_affine", "magnitude_context_affine", "input_energy_residual_affine"):
        profile = Profile(weight_bits=16, dac_bits=16, adc_bits=14)
        projections = {name: TiledProjection(modules[name].weight, modules[name].bias,
                                              bounds[name] * 1.25, profile, calibration_fixture.get("seed", 8181))
                       for name in names}
        replacements = [(modules[name], lambda x, projection=projection: projection(x, ideal=False))
                        for name, projection in projections.items()]
        with replace_forwards(replacements):
            calibration_candidate = capture_module_outputs(model, tokenizer, modules,
                                                            calibration_fixture["calibration"], "cpu")
        records = {}
        for name, projection in projections.items():
            if mode == "global_affine":
                scale, correction = fit_affine(references[name], calibration_candidate[name])
                projection.output_scale, projection.output_correction = scale, correction
                records[name] = {"threshold": None, "bins": 1}
            elif mode == "magnitude_context_affine":
                provisional = calibration_candidate[name]
                norms = provisional.norm(dim=1)
                threshold = float(norms.median())
                masks = (norms < threshold, norms >= threshold)
                scales, corrections, counts = [], [], []
                for mask in masks:
                    if int(mask.sum()) < 3:
                        raise RuntimeError(f"context calibration bin too small for {name}")
                    scale, correction = fit_affine(references[name][mask], provisional[mask])
                    scales.append(scale)
                    corrections.append(correction)
                    counts.append(int(mask.sum()))
                projection.context_threshold = threshold
                projection.context_scale = torch.stack(scales)
                projection.context_correction = torch.stack(corrections)
                records[name] = {"threshold": threshold, "bins": 2, "bin_counts": counts}
            else:
                scale, correction, residual_scale, center = fit_input_energy_residual(
                    references[name], calibration_candidate[name], input_energies[name])
                projection.output_scale, projection.output_correction = scale, correction
                projection.input_energy_residual_scale = residual_scale
                projection.input_energy_residual_center = center
                records[name] = {"bins": 1, "conditioning": "incoming activation L2 norm", "center": float(center)}
            clear_projection(projection)
        for dataset, fixture in datasets.items():
            with replace_forwards(replacements):
                candidate = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
            quality = compare(baselines[dataset], candidate)
            screen = fixture["exploratory_screen"]
            quality["screen_pass"] = (quality["nll_increase_nats"] <= screen["maximum_nll_increase_nats"]
                                       and quality["teacher_forced_argmax_agreement"] >= screen["minimum_teacher_forced_argmax_agreement"])
            results[f"{mode}_{dataset}"] = {"mode": mode, "dataset": dataset, "quality": quality,
                                             "calibration": records,
                                             "profile": {"weight_bits": 16, "dac_bits": 16, "adc_bits": 14,
                                                         "range_multiplier": 1.25}}
    sources = {"calibration_fixture": {"path": str(args.calibration_fixture), "sha256": digest(args.calibration_fixture)},
               "original_fixture": {"path": str(args.original_fixture), "sha256": digest(args.original_fixture)},
               "stress_fixture": {"path": str(args.stress_fixture), "sha256": digest(args.stress_fixture)},
               "runner": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}}
    if args.third_fixture:
        sources["third_fixture"] = {"path": str(args.third_fixture), "sha256": digest(args.third_fixture)}
    report = {
        "schema_version": "gpt2-context-transfer-profile-v0.1",
        "result_type": "local_magnitude_context_transfer_profile_comparison",
        "sources": sources,
        "model_revision": PINNED_REVISION, "target_modules": names, "results": results,
        "passing_results": [name for name, row in results.items() if row["quality"]["screen_pass"]],
        "analog_authorized": False,
        "claim_boundary": "Local CPU context-aware transfer comparison only; no measured hardware latency, energy, silicon yield, or analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "context_transfer_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        {"path": str(args.calibration_fixture), "sha256": digest(args.calibration_fixture)},
        {"path": str(args.original_fixture), "sha256": digest(args.original_fixture)},
        {"path": str(args.stress_fixture), "sha256": digest(args.stress_fixture)},
        *([{"path": str(args.third_fixture), "sha256": digest(args.third_fixture)}] if args.third_fixture else []),
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "passing_results": report["passing_results"]}, sort_keys=True))


if __name__ == "__main__":
    main()
