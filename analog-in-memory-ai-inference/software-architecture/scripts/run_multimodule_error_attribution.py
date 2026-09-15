#!/usr/bin/env python3
"""Attribute calibrated multi-module replay error to module outputs and final logits."""

from __future__ import annotations

import argparse
import hashlib
import json
from contextlib import contextmanager
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_gpt2_multimodule_replay import (PINNED_REVISION, affine_fit,
                                         capture_activation_bounds,
                                         capture_module_outputs, clear_projection,
                                         replace_forwards)
from tiled_projection_model import Profile, TiledProjection


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@contextmanager
def capture_hooks(modules):
    captured = {name: [] for name in modules}
    handles = []
    for name, module in modules.items():
        def observe(_module, _inputs, output, module_name=name):
            if isinstance(output, tuple):
                output = output[0]
            captured[module_name].append(output.detach().cpu().reshape(-1, output.shape[-1]))
        handles.append(module.register_forward_hook(observe))
    try:
        yield captured
    finally:
        for handle in handles:
            handle.remove()


def forward_capture(model, tokenizer, modules, texts, replacements=None):
    context = replace_forwards(replacements) if replacements else null_context()
    with context, capture_hooks(modules) as captured:
        logits = []
        with torch.inference_mode():
            for text in texts:
                encoded = {key: value for key, value in tokenizer(text, return_tensors="pt").items()}
                logits.append(model(**encoded, use_cache=False).logits.detach().cpu().float())
    return {name: torch.cat(rows, dim=0) for name, rows in captured.items()}, logits


@contextmanager
def null_context():
    yield


def metrics(reference_outputs, candidate_outputs, reference_logits, candidate_logits):
    module_metrics = {}
    for name in reference_outputs:
        delta = candidate_outputs[name].double() - reference_outputs[name].double()
        module_metrics[name] = {
            "output_rows": int(delta.shape[0]),
            "output_relative_l2": float(torch.linalg.vector_norm(delta) /
                                         torch.linalg.vector_norm(reference_outputs[name].double()).clamp_min(1e-12)),
            "output_max_abs_error": float(delta.abs().max()),
        }
    logit_delta = torch.cat([candidate - reference for reference, candidate in zip(reference_logits, candidate_logits)], dim=1)
    reference_flat = torch.cat(reference_logits, dim=1)
    return {
        "modules": module_metrics,
        "final_logit_relative_l2": float(torch.linalg.vector_norm(logit_delta) /
                                          torch.linalg.vector_norm(reference_flat).clamp_min(1e-12)),
        "final_logit_max_abs_error": float(logit_delta.abs().max()),
        "final_argmax_disagreement": float((torch.cat([x.argmax(-1) for x in reference_logits], dim=1) !=
                                             torch.cat([x.argmax(-1) for x in candidate_logits], dim=1)).float().mean()),
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
    model = AutoModelForCausalLM.from_pretrained(args.snapshot_path, local_files_only=True,
                                                 use_safetensors=True, attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(args.snapshot_path, local_files_only=True)
    modules = {name: model.get_submodule(name) for name in fixture["target_modules"]}
    bounds = capture_activation_bounds(model, tokenizer, modules, fixture["calibration"], "cpu")
    calibration_reference, _ = forward_capture(model, tokenizer, modules, fixture["calibration"])
    reference_outputs, reference_logits = forward_capture(model, tokenizer, modules, fixture["evaluation"])
    names = list(modules)
    scenarios = {
        "c_fc_only": [names[0]],
        "c_proj_only": [names[1]],
        "attn_only": [names[2]],
        "c_proj_digital_mixed": [names[0], names[2]],
        "full_three_module": names,
    }
    results = {}
    for scenario_name, selected in scenarios.items():
        projections = {
            name: TiledProjection(modules[name].weight, modules[name].bias, bounds[name],
                                  Profile(adc_bits=12), fixture["seed"])
            for name in selected
        }
        replacements = [(modules[name], lambda x, projection=projection: projection(x, ideal=False))
                        for name, projection in projections.items()]
        calibration_candidate, _ = forward_capture(model, tokenizer, modules, fixture["calibration"], replacements)
        for name, projection in projections.items():
            scale, correction = affine_fit(calibration_reference[name], calibration_candidate[name])
            projection.output_scale = scale
            projection.output_correction = correction
            clear_projection(projection)
        candidate_outputs, candidate_logits = forward_capture(model, tokenizer, modules, fixture["evaluation"], replacements)
        results[scenario_name] = {
            "analog_modules": selected,
            "digital_modules": [name for name in names if name not in selected],
            "metrics": metrics(reference_outputs, candidate_outputs, reference_logits, candidate_logits),
            "trace_events": {name: len(projection.trace) for name, projection in projections.items()},
            "claim_boundary": "Local calibrated CPU replay; output and logit differences are not measured hardware behavior.",
        }
    individual_logit_error = sum(row["metrics"]["final_logit_relative_l2"]
                                 for key, row in results.items() if key.endswith("_only"))
    full_error = results["full_three_module"]["metrics"]["final_logit_relative_l2"]
    report = {
        "schema_version": "gpt2-multimodule-error-attribution-v0.1",
        "result_type": "local_multi_module_output_to_logit_error_attribution",
        "source": {"fixture": {"path": str(args.fixture), "sha256": digest(args.fixture)},
                   "runner": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}},
        "model_revision": fixture["revision"], "target_modules": names,
        "calibration_split": fixture["calibration"], "evaluation_split": fixture["evaluation"],
        "activation_bounds": bounds, "adc_bits": 12, "calibrated": True,
        "scenarios": results,
        "interaction_summary": {
            "sum_of_isolated_final_logit_relative_l2": individual_logit_error,
            "full_route_final_logit_relative_l2": full_error,
            "full_to_isolated_sum_ratio": full_error / max(individual_logit_error, 1e-12),
            "interpretation": "Ratio above one indicates non-additive propagation; this is attribution evidence, not a causal hardware proof.",
        },
        "claim_boundary": "Local CPU attribution only; no measured hardware latency, energy, silicon yield, or analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "error_attribution_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    manifest = {"files": [{"path": str(report_path), "sha256": digest(report_path)},
                          {"path": str(args.fixture), "sha256": digest(args.fixture)},
                          {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}]}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "scenarios": len(results),
                      "interaction_ratio": report["interaction_summary"]["full_to_isolated_sum_ratio"]}, sort_keys=True))


if __name__ == "__main__":
    main()
