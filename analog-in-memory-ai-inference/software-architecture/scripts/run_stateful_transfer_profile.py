#!/usr/bin/env python3
"""Compare affine and sequence-history-aware calibrated transfer profiles."""

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


def split_rows(tensor, texts, tokenizer):
    result, start = [], 0
    for text in texts:
        count = int(tokenizer(text, return_tensors="pt")["input_ids"].shape[1])
        result.append(tensor[start:start + count])
        start += count
    return result


def fit_stateful(reference_parts, candidate_parts):
    design_rows, target_rows = [], []
    for reference, candidate in zip(reference_parts, candidate_parts):
        previous = torch.zeros_like(candidate)
        previous[1:] = candidate[:-1]
        design_rows.append(torch.stack((candidate, torch.ones_like(candidate), previous), dim=-1).permute(1, 0, 2))
        target_rows.append(reference.transpose(0, 1))
    design = torch.cat(design_rows, dim=1).double()
    target = torch.cat(target_rows, dim=1).double()
    coefficients = torch.linalg.lstsq(design, target).solution
    return coefficients[:, 0].float(), coefficients[:, 1].float(), coefficients[:, 2].float()


def fit_stateful_second_order(reference_parts, candidate_parts):
    design_rows, target_rows = [], []
    for reference, candidate in zip(reference_parts, candidate_parts):
        previous = torch.zeros_like(candidate)
        previous2 = torch.zeros_like(candidate)
        if candidate.shape[0] > 1:
            previous[1:] = candidate[:-1]
        if candidate.shape[0] > 2:
            previous2[2:] = candidate[:-2]
        design_rows.append(torch.stack((candidate, torch.ones_like(candidate), previous, previous2), dim=-1).permute(1, 0, 2))
        target_rows.append(reference.transpose(0, 1))
    design = torch.cat(design_rows, dim=1).double()
    target = torch.cat(target_rows, dim=1).double()
    coefficients = torch.linalg.lstsq(design, target).solution
    return (coefficients[:, 0].float(), coefficients[:, 1].float(),
            coefficients[:, 2].float(), coefficients[:, 3].float())


def fit_affine(reference, candidate):
    reference, candidate = reference.double(), candidate.double()
    reference_mean, candidate_mean = reference.mean(0), candidate.mean(0)
    centered_reference, centered_candidate = reference - reference_mean, candidate - candidate_mean
    variance = (centered_candidate * centered_candidate).sum(0).clamp_min(1e-12)
    scale = (centered_candidate * centered_reference).sum(0) / variance
    return scale.float(), (reference_mean - scale * candidate_mean).float()


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
    cal = json.loads(args.calibration_fixture.read_text(encoding="utf-8"))
    original = json.loads(args.original_fixture.read_text(encoding="utf-8"))
    stress = json.loads(args.stress_fixture.read_text(encoding="utf-8"))
    third = json.loads(args.third_fixture.read_text(encoding="utf-8")) if args.third_fixture else None
    fixtures = (cal, original, stress) + ((third,) if third else ())
    if any(item["revision"] != PINNED_REVISION for item in fixtures):
        raise SystemExit("all fixtures must use the pinned revision")
    evaluation_sets = [set(item["evaluation"]) for item in (original, stress) + ((third,) if third else ())]
    if set(cal["calibration"]) & set.union(*evaluation_sets):
        raise SystemExit("calibration and evaluation splits overlap")
    if any(left & right for index, left in enumerate(evaluation_sets) for right in evaluation_sets[index + 1:]):
        raise SystemExit("evaluation splits overlap")
    torch.set_num_threads(args.threads)
    model = AutoModelForCausalLM.from_pretrained(args.snapshot_path, local_files_only=True,
                                                 use_safetensors=True, attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(args.snapshot_path, local_files_only=True)
    modules = {name: model.get_submodule(name) for name in cal["target_modules"]}
    names = list(modules)
    bounds = capture_activation_bounds(model, tokenizer, modules, cal["calibration"], "cpu")
    references = capture_module_outputs(model, tokenizer, modules, cal["calibration"], "cpu")
    datasets = {"original": original, "stress": stress}
    if third:
        datasets["third_holdout"] = third
    baselines = {name: evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
                 for name, fixture in datasets.items()}
    results = {}
    profile = Profile(weight_bits=16, dac_bits=16, adc_bits=14)
    for mode in ("affine", "stateful_previous_token", "stateful_previous_two_tokens"):
        projections = {name: TiledProjection(modules[name].weight, modules[name].bias, bounds[name] * 1.25,
                                              profile, cal.get("seed", 8181)) for name in names}
        replacements = [(modules[name], lambda x, projection=projection: projection(x, ideal=False))
                        for name, projection in projections.items()]
        with replace_forwards(replacements):
            calibration_candidate = capture_module_outputs(model, tokenizer, modules, cal["calibration"], "cpu")
        calibration_records = {}
        for name, projection in projections.items():
            if mode == "affine":
                gain, offset = fit_affine(references[name], calibration_candidate[name])
                projection.output_scale, projection.output_correction = gain, offset
                calibration_records[name] = {"bins": 1}
            elif mode == "stateful_previous_token":
                gain, offset, previous_gain = fit_stateful(split_rows(references[name], cal["calibration"], tokenizer),
                                                           split_rows(calibration_candidate[name], cal["calibration"], tokenizer))
                projection.output_scale, projection.output_correction = gain, offset
                projection.stateful_previous_scale = previous_gain
                calibration_records[name] = {"bins": 1, "history_term": "previous provisional output row"}
            else:
                gain, offset, previous_gain, previous2_gain = fit_stateful_second_order(
                    split_rows(references[name], cal["calibration"], tokenizer),
                    split_rows(calibration_candidate[name], cal["calibration"], tokenizer))
                projection.output_scale, projection.output_correction = gain, offset
                projection.stateful_previous_scale = previous_gain
                projection.stateful_previous2_scale = previous2_gain
                calibration_records[name] = {"bins": 1, "history_term": "two previous provisional output rows"}
            clear_projection(projection)
        for dataset, fixture in datasets.items():
            with replace_forwards(replacements):
                candidate = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
            quality = compare(baselines[dataset], candidate)
            screen = fixture["exploratory_screen"]
            quality["screen_pass"] = (quality["nll_increase_nats"] <= screen["maximum_nll_increase_nats"]
                                       and quality["teacher_forced_argmax_agreement"] >= screen["minimum_teacher_forced_argmax_agreement"])
            results[f"{mode}_{dataset}"] = {"mode": mode, "dataset": dataset, "quality": quality,
                                             "calibration": calibration_records,
                                             "profile": {"weight_bits": 16, "dac_bits": 16, "adc_bits": 14,
                                                         "range_multiplier": 1.25,
                                                         "history_order": 2 if mode == "stateful_previous_two_tokens" else 1 if mode == "stateful_previous_token" else 0}}
    sources = {"calibration_fixture": {"path": str(args.calibration_fixture), "sha256": digest(args.calibration_fixture)},
               "original_fixture": {"path": str(args.original_fixture), "sha256": digest(args.original_fixture)},
               "stress_fixture": {"path": str(args.stress_fixture), "sha256": digest(args.stress_fixture)},
               "runner": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}}
    if args.third_fixture:
        sources["third_fixture"] = {"path": str(args.third_fixture), "sha256": digest(args.third_fixture)}
    report = {
        "schema_version": "gpt2-stateful-transfer-profile-v0.1",
        "result_type": "local_sequence_history_transfer_profile_comparison",
        "sources": sources,
        "model_revision": PINNED_REVISION, "target_modules": names, "results": results,
        "passing_results": [name for name, row in results.items() if row["quality"]["screen_pass"]],
        "analog_authorized": False,
        "claim_boundary": "Local CPU stateful transfer comparison only; no measured hardware latency, energy, silicon yield, or analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "stateful_transfer_report.json"
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
