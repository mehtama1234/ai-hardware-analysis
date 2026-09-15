#!/usr/bin/env python3
"""Compare affine and quadratic calibrated transfer models on original and stress splits."""

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


def fit_quadratic(reference: torch.Tensor, candidate: torch.Tensor):
    x = candidate.double()
    y = reference.double()
    design = torch.stack((x.square(), x, torch.ones_like(x)), dim=-1).permute(1, 0, 2)
    coefficients = torch.linalg.lstsq(design, y.transpose(0, 1)).solution
    return coefficients[:, 0].float(), coefficients[:, 1].float(), coefficients[:, 2].float()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-path", type=Path, required=True)
    parser.add_argument("--calibration-fixture", type=Path, required=True)
    parser.add_argument("--original-fixture", type=Path, required=True)
    parser.add_argument("--stress-fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    calibration_fixture = json.loads(args.calibration_fixture.read_text(encoding="utf-8"))
    original_fixture = json.loads(args.original_fixture.read_text(encoding="utf-8"))
    stress_fixture = json.loads(args.stress_fixture.read_text(encoding="utf-8"))
    if any(fixture["revision"] != PINNED_REVISION for fixture in (calibration_fixture, original_fixture, stress_fixture)):
        raise SystemExit("all fixtures must use the pinned revision")
    if set(calibration_fixture["calibration"]) & (set(original_fixture["evaluation"]) | set(stress_fixture["evaluation"])):
        raise SystemExit("calibration and evaluation splits overlap")
    torch.set_num_threads(args.threads)
    model = AutoModelForCausalLM.from_pretrained(args.snapshot_path, local_files_only=True,
                                                 use_safetensors=True, attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(args.snapshot_path, local_files_only=True)
    modules = {name: model.get_submodule(name) for name in calibration_fixture["target_modules"]}
    names = list(modules)
    bounds = capture_activation_bounds(model, tokenizer, modules, calibration_fixture["calibration"], "cpu")
    references = capture_module_outputs(model, tokenizer, modules, calibration_fixture["calibration"], "cpu")
    datasets = {"original": original_fixture, "stress": stress_fixture}
    baselines = {label: evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
                 for label, fixture in datasets.items()}
    results = {}
    profile = Profile(weight_bits=16, dac_bits=16, adc_bits=14)
    for mode in ("affine", "quadratic"):
        projections = {name: TiledProjection(modules[name].weight, modules[name].bias,
                                              bounds[name] * 1.25, profile, original_fixture.get("seed", 8181))
                       for name in names}
        replacements = [(modules[name], lambda x, projection=projection: projection(x, ideal=False))
                        for name, projection in projections.items()]
        with replace_forwards(replacements):
            calibration_candidate = capture_module_outputs(model, tokenizer, modules,
                                                            calibration_fixture["calibration"], "cpu")
        calibration_records = {}
        for name, projection in projections.items():
            if mode == "affine":
                reference = references[name].double()
                candidate = calibration_candidate[name].double()
                centered_reference = reference - reference.mean(dim=0)
                centered_candidate = candidate - candidate.mean(dim=0)
                variance = (centered_candidate * centered_candidate).sum(dim=0).clamp_min(1e-12)
                gain = ((centered_candidate * centered_reference).sum(dim=0) / variance).float()
                offset = (reference.mean(dim=0) - gain.double() * candidate.mean(dim=0)).float()
                projection.output_scale, projection.output_correction = gain, offset
                fit_prediction = candidate * gain.double() + offset.double()
            else:
                quadratic, gain, offset = fit_quadratic(references[name], calibration_candidate[name])
                projection.output_quadratic = quadratic
                projection.output_scale, projection.output_correction = gain, offset
                candidate = calibration_candidate[name].double()
                fit_prediction = candidate.square() * quadratic.double() + candidate * gain.double() + offset.double()
            calibration_records[name] = {
                "relative_l2_after": float(torch.linalg.vector_norm(fit_prediction - references[name].double()) /
                                            torch.linalg.vector_norm(references[name].double()).clamp_min(1e-12)),
            }
            clear_projection(projection)
        for dataset, fixture in datasets.items():
            with replace_forwards(replacements):
                candidate = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
            quality = compare(baselines[dataset], candidate)
            screen = fixture["exploratory_screen"]
            quality["screen_pass"] = (quality["nll_increase_nats"] <= screen["maximum_nll_increase_nats"]
                                       and quality["teacher_forced_argmax_agreement"] >= screen["minimum_teacher_forced_argmax_agreement"])
            results[f"{mode}_{dataset}"] = {"mode": mode, "dataset": dataset,
                                             "profile": {"weight_bits": 16, "dac_bits": 16, "adc_bits": 14,
                                                         "range_multiplier": 1.25},
                                             "quality": quality, "calibration": calibration_records}
    report = {
        "schema_version": "gpt2-multimodule-transfer-model-sweep-v0.1",
        "result_type": "local_calibrated_transfer_model_comparison",
        "sources": {"calibration_fixture": {"path": str(args.calibration_fixture), "sha256": digest(args.calibration_fixture)},
                    "original_fixture": {"path": str(args.original_fixture), "sha256": digest(args.original_fixture)},
                    "stress_fixture": {"path": str(args.stress_fixture), "sha256": digest(args.stress_fixture)},
                    "runner": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}},
        "model_revision": PINNED_REVISION, "target_modules": names,
        "results": results,
        "passing_results": [name for name, row in results.items() if row["quality"]["screen_pass"]],
        "analog_authorized": False,
        "claim_boundary": "Local CPU transfer-model comparison only; no measured hardware latency, energy, silicon yield, or analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "transfer_model_sweep_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        {"path": str(args.calibration_fixture), "sha256": digest(args.calibration_fixture)},
        {"path": str(args.original_fixture), "sha256": digest(args.original_fixture)},
        {"path": str(args.stress_fixture), "sha256": digest(args.stress_fixture)},
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "passing_results": report["passing_results"]}, sort_keys=True))


if __name__ == "__main__":
    main()
