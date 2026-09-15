#!/usr/bin/env python3
"""Test c_proj-only ADC resolution mitigation with fixed stateful calibration."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_gpt2_hybrid_evaluation import compare, evaluate
from run_gpt2_multimodule_replay import (PINNED_REVISION, capture_activation_bounds,
                                         capture_module_outputs, clear_projection,
                                         replace_forwards)
from run_stateful_transfer_profile import fit_stateful, split_rows
from tiled_projection_model import Profile, TiledProjection


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit_quadratic(reference, candidate):
    design = torch.stack((candidate, torch.ones_like(candidate), candidate.square()), dim=-1).double()
    coefficients = []
    for index in range(candidate.shape[1]):
        coefficients.append(torch.linalg.lstsq(design[:, index, :], reference[:, index].double()).solution)
    coefficients = torch.stack(coefficients)
    return coefficients[:, 0].float(), coefficients[:, 1].float(), coefficients[:, 2].float()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-path", type=Path, required=True)
    parser.add_argument("--calibration-fixture", type=Path, required=True)
    parser.add_argument("--original-fixture", type=Path, required=True)
    parser.add_argument("--stress-fixture", type=Path, required=True)
    parser.add_argument("--third-fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    fixtures = [json.loads(path.read_text(encoding="utf-8")) for path in
                (args.calibration_fixture, args.original_fixture, args.stress_fixture, args.third_fixture)]
    if any(fixture["revision"] != PINNED_REVISION for fixture in fixtures):
        raise SystemExit("all fixtures must use the pinned revision")
    calibration = fixtures[0]
    evaluation_fixtures = {"original": fixtures[1], "stress": fixtures[2], "third_holdout": fixtures[3]}
    evaluation_sets = [set(fixture["evaluation"]) for fixture in evaluation_fixtures.values()]
    if set(calibration["calibration"]) & set.union(*evaluation_sets) or any(
            left & right for index, left in enumerate(evaluation_sets) for right in evaluation_sets[index + 1:]):
        raise SystemExit("calibration and evaluation splits overlap")
    torch.set_num_threads(args.threads)
    model = AutoModelForCausalLM.from_pretrained(args.snapshot_path, local_files_only=True,
                                                 use_safetensors=True, attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(args.snapshot_path, local_files_only=True)
    modules = {name: model.get_submodule(name) for name in calibration["target_modules"]}
    names = list(modules)
    bounds = capture_activation_bounds(model, tokenizer, modules, calibration["calibration"], "cpu")
    references = capture_module_outputs(model, tokenizer, modules, calibration["calibration"], "cpu")
    baselines = {label: evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
                 for label, fixture in evaluation_fixtures.items()}
    designs = {"uniform_adc14_control": {name: 14 for name in names},
               "c_proj_adc16_only": {names[0]: 14, names[1]: 16, names[2]: 14},
               "c_proj_quadratic_only": {name: 14 for name in names}}
    settling = {"uniform_adc14_control": 0.0, "c_proj_adc16_only": 0.0,
                "c_proj_quadratic_only": 0.0, "c_proj_settling_001": 0.001,
                "c_proj_settling_01": 0.01, "c_proj_settling_05": 0.05,
                "c_proj_state_machine_095_01": 0.01, "c_proj_state_machine_1_01": 0.01}
    charge = {label: 1.0 for label in settling}
    charge.update({"c_proj_state_machine_095_01": 0.95, "c_proj_state_machine_1_01": 1.0})
    designs.update({label: {name: 14 for name in names} for label in
                    ("c_proj_settling_001", "c_proj_settling_01", "c_proj_settling_05",
                     "c_proj_state_machine_095_01", "c_proj_state_machine_1_01")})
    results = {}
    for label, adc_bits in designs.items():
        profile = Profile(weight_bits=16, dac_bits=16, adc_bits=14)
        projections = {name: TiledProjection(modules[name].weight, modules[name].bias, bounds[name] * 1.25,
                                              Profile(weight_bits=16, dac_bits=16, adc_bits=adc_bits[name]),
                                              calibration.get("seed", 8181),
                                              settling_fraction=settling[label] if name == names[1] else 0.0,
                                              charge_fraction=charge[label] if name == names[1] else 1.0)
                      for name in names}
        replacements = [(modules[name], lambda x, projection=projection: projection(x, ideal=False))
                        for name, projection in projections.items()]
        with replace_forwards(replacements):
            calibrated = capture_module_outputs(model, tokenizer, modules, calibration["calibration"], "cpu")
        records = {}
        for name, projection in projections.items():
            if label == "c_proj_quadratic_only" and name == names[1]:
                gain, offset, quadratic = fit_quadratic(references[name], calibrated[name])
                projection.output_scale, projection.output_correction = gain, offset
                projection.output_quadratic = quadratic
                records[name] = {"adc_bits": adc_bits[name], "transfer_model": "per-channel quadratic"}
            else:
                gain, offset, previous_gain = fit_stateful(
                    split_rows(references[name], calibration["calibration"], tokenizer),
                    split_rows(calibrated[name], calibration["calibration"], tokenizer))
                projection.output_scale, projection.output_correction = gain, offset
                projection.stateful_previous_scale = previous_gain
                records[name] = {"adc_bits": adc_bits[name], "history_term": "previous provisional output row",
                                 "settling_fraction": settling[label] if name == names[1] else 0.0,
                                 "charge_fraction": charge[label] if name == names[1] else 1.0}
            clear_projection(projection)
        for dataset, fixture in evaluation_fixtures.items():
            with replace_forwards(replacements):
                candidate = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device="cpu")
            quality = compare(baselines[dataset], candidate)
            screen = fixture["exploratory_screen"]
            quality["screen_pass"] = (quality["nll_increase_nats"] <= screen["maximum_nll_increase_nats"]
                                       and quality["teacher_forced_argmax_agreement"] >= screen["minimum_teacher_forced_argmax_agreement"])
            results[f"{label}_{dataset}"] = {"design": label, "dataset": dataset, "quality": quality,
                                               "calibration": records, "adc_bits": adc_bits}
    sources = {label: {"path": str(path), "sha256": digest(path)} for label, path in zip(
        ("calibration_fixture", "original_fixture", "stress_fixture", "third_fixture"),
        (args.calibration_fixture, args.original_fixture, args.stress_fixture, args.third_fixture))}
    sources["runner"] = {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}
    report = {"schema_version": "gpt2-targeted-cproj-adc-mitigation-v0.1",
              "result_type": "local_cproj_only_adc_resolution_mitigation",
              "sources": sources, "model_revision": PINNED_REVISION, "target_modules": names,
              "results": results,
              "decision": "c_proj_adc16_does_not_generalize" if not all(
                  results[f"c_proj_adc16_only_{dataset}"]["quality"]["screen_pass"] for dataset in evaluation_fixtures) else "c_proj_adc16_candidate_passes_all_splits",
              "quadratic_decision": "c_proj_quadratic_does_not_generalize" if not all(
                  results[f"c_proj_quadratic_only_{dataset}"]["quality"]["screen_pass"] for dataset in evaluation_fixtures) else "c_proj_quadratic_candidate_passes_all_splits",
              "settling_decisions": {label: "passes_all_splits" if all(
                  results[f"{label}_{dataset}"]["quality"]["screen_pass"] for dataset in evaluation_fixtures) else "does_not_generalize"
                  for label in ("c_proj_settling_001", "c_proj_settling_01", "c_proj_settling_05",
                                "c_proj_state_machine_095_01", "c_proj_state_machine_1_01")},
              "analog_authorized": False,
              "claim_boundary": "Local CPU targeted c_proj ADC mitigation only; no measured hardware latency, energy, silicon yield, or analog authorization."}
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "targeted_cproj_adc_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        *[{"path": str(path), "sha256": digest(path)} for path in
          (args.calibration_fixture, args.original_fixture, args.stress_fixture, args.third_fixture)],
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "decision": report["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
