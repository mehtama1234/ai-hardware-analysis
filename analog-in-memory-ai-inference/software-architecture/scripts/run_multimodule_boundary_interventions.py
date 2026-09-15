#!/usr/bin/env python3
"""Measure downstream propagation of calibrated module-boundary perturbations."""

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
def null_context():
    yield


def forward_capture(model, tokenizer, modules, texts, replacements=None, intervention=None):
    captured = {name: [] for name in modules}
    handles = []
    if intervention:
        source, chunks = intervention
        state = {"index": 0}

        def inject(_module, _inputs, output):
            delta = chunks[state["index"]]
            state["index"] += 1
            return output + delta

        handles.append(modules[source].register_forward_hook(inject))
    for name, module in modules.items():
        def observe(_module, _inputs, output, module_name=name):
            if isinstance(output, tuple):
                output = output[0]
            captured[module_name].append(output.detach().cpu().reshape(-1, output.shape[-1]))
        handles.append(module.register_forward_hook(observe))
    logits = []
    context = replace_forwards(replacements) if replacements else null_context()
    try:
        with context, torch.inference_mode():
            for text in texts:
                encoded = tokenizer(text, return_tensors="pt")
                logits.append(model(**encoded, use_cache=False).logits.detach().cpu().float())
    finally:
        for handle in handles:
            handle.remove()
    return {name: torch.cat(rows, dim=0) for name, rows in captured.items()}, logits


def split_rows(tensor, texts, tokenizer):
    rows = []
    for text in texts:
        rows.append(int(tokenizer(text, return_tensors="pt")["input_ids"].shape[1]))
    output = []
    start = 0
    for count in rows:
        output.append(tensor[start:start + count])
        start += count
    return output


def relative(a, b):
    return float(torch.linalg.vector_norm(a.double() - b.double()) /
                 torch.linalg.vector_norm(b.double()).clamp_min(1e-12))


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
    names = list(modules)
    bounds = capture_activation_bounds(model, tokenizer, modules, fixture["calibration"], "cpu")
    calibration_reference, _ = forward_capture(model, tokenizer, modules, fixture["calibration"])
    native_outputs, native_logits = forward_capture(model, tokenizer, modules, fixture["evaluation"])
    scales = (0.25, 0.5, 1.0, 2.0)
    results = {}
    for source in names:
        projection = TiledProjection(modules[source].weight, modules[source].bias, bounds[source],
                                     Profile(adc_bits=12), fixture["seed"])
        replacement = [(modules[source], lambda x, projection=projection: projection(x, ideal=False))]
        calibration_candidate, _ = forward_capture(model, tokenizer, modules, fixture["calibration"], replacements=replacement)
        scale, correction = affine_fit(calibration_reference[source], calibration_candidate[source])
        projection.output_scale = scale
        projection.output_correction = correction
        clear_projection(projection)
        calibrated_outputs, _ = forward_capture(model, tokenizer, modules, fixture["evaluation"], replacements=replacement)
        deltas = split_rows(calibrated_outputs[source] - native_outputs[source], fixture["evaluation"], tokenizer)
        source_rows = {}
        for amplitude in scales:
            intervention_deltas = [delta * amplitude for delta in deltas]
            outputs, logits = forward_capture(model, tokenizer, modules,
                                               fixture["evaluation"], intervention=(source, intervention_deltas))
            downstream = {name: relative(outputs[name], native_outputs[name]) for name in names}
            logit_delta = torch.cat([candidate - reference for reference, candidate in zip(native_logits, logits)], dim=1)
            reference_flat = torch.cat(native_logits, dim=1)
            source_rows[str(amplitude)] = {
                "downstream_output_relative_l2": downstream,
                "final_logit_relative_l2": float(torch.linalg.vector_norm(logit_delta) /
                                                  torch.linalg.vector_norm(reference_flat).clamp_min(1e-12)),
                "final_logit_max_abs_error": float(logit_delta.abs().max()),
                "final_argmax_disagreement": float((torch.cat([x.argmax(-1) for x in native_logits], dim=1) !=
                                                     torch.cat([x.argmax(-1) for x in logits], dim=1)).float().mean()),
            }
        results[source] = {
            "source_module": source,
            "calibrated_adc12_output_relative_l2": relative(calibrated_outputs[source], native_outputs[source]),
            "interventions": source_rows,
            "claim_boundary": "Local CPU boundary injection; perturbation propagation is not a causal hardware measurement.",
        }
    report = {
        "schema_version": "gpt2-multimodule-boundary-intervention-v0.1",
        "result_type": "local_module_boundary_perturbation_propagation",
        "source": {"fixture": {"path": str(args.fixture), "sha256": digest(args.fixture)},
                   "runner": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}},
        "model_revision": fixture["revision"], "target_modules": names,
        "calibration_split": fixture["calibration"], "evaluation_split": fixture["evaluation"],
        "adc_bits": 12, "calibrated": True, "amplitudes": scales,
        "activation_bounds": bounds, "results": results,
        "claim_boundary": "Local CPU boundary intervention only; no measured hardware latency, energy, silicon yield, causal hardware, or analog authorization claim.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "boundary_intervention_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        {"path": str(args.fixture), "sha256": digest(args.fixture)},
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "modules": len(results), "amplitudes": len(scales)}, sort_keys=True))


if __name__ == "__main__":
    main()
