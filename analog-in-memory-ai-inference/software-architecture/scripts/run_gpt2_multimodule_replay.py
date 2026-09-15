#!/usr/bin/env python3
"""Replay one frozen GPT-2 workload through several provisional tiled modules."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_gpt2_hybrid_evaluation import compare, evaluate
from tiled_projection_model import Profile, TiledProjection


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "experiments/gpt2-hybrid-v1/fixture-multimodule-v1.json"
PINNED_REVISION = "607a30d783dfa663caf39e06633721c8d4cfcd7e"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source(path: Path) -> dict[str, str]:
    return {"path": str(path), "sha256": sha256(path)}


@contextmanager
def replace_forwards(replacements):
    originals = []
    try:
        for module, replacement in replacements:
            originals.append((module, module.forward))
            module.forward = replacement
        yield
    finally:
        for module, original in originals:
            module.forward = original


def capture_activation_bounds(model, tokenizer, modules, texts, device):
    bounds = {name: 0.0 for name in modules}
    handles = []
    for name, module in modules.items():
        def observe(_module, inputs, module_name=name):
            bounds[module_name] = max(bounds[module_name], float(inputs[0].abs().max()))
        handles.append(module.register_forward_pre_hook(observe))
    try:
        with torch.inference_mode():
            for text in texts:
                encoded = {key: value.to(device) for key, value in tokenizer(text, return_tensors="pt").items()}
                model(**encoded, use_cache=False)
    finally:
        for handle in handles:
            handle.remove()
    return bounds


def capture_module_outputs(model, tokenizer, modules, texts, device):
    """Capture one native or replaced output tensor per target module."""
    captured = {name: [] for name in modules}
    handles = []
    for name, module in modules.items():
        def observe(_module, _inputs, output, module_name=name):
            if isinstance(output, tuple):
                output = output[0]
            captured[module_name].append(output.detach().cpu().reshape(-1, output.shape[-1]))
        handles.append(module.register_forward_hook(observe))
    try:
        with torch.inference_mode():
            for text in texts:
                encoded = {key: value.to(device) for key, value in tokenizer(text, return_tensors="pt").items()}
                model(**encoded, use_cache=False)
    finally:
        for handle in handles:
            handle.remove()
    return {name: torch.cat(rows, dim=0) for name, rows in captured.items()}


def affine_fit(reference: torch.Tensor, candidate: torch.Tensor):
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


def clear_projection(projection: TiledProjection):
    projection.output_vectors.clear()
    projection.trace.clear()


def flatten_outputs(projection: TiledProjection) -> np.ndarray:
    if not projection.output_vectors:
        raise RuntimeError("projection produced no output vectors")
    return np.concatenate(projection.output_vectors, axis=0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-path", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    if fixture["revision"] != PINNED_REVISION or len(fixture["target_modules"]) < 2:
        raise SystemExit("fixture must use the pinned revision and at least two target modules")
    torch.set_num_threads(args.threads)
    torch.manual_seed(fixture["seed"])
    device = torch.device("cpu")
    snapshot = args.snapshot_path
    model = AutoModelForCausalLM.from_pretrained(snapshot, local_files_only=True,
                                                 use_safetensors=True, attn_implementation="eager").to(device).eval()
    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
    modules = {name: model.get_submodule(name) for name in fixture["target_modules"]}
    bounds = capture_activation_bounds(model, tokenizer, modules, fixture["calibration"], device)
    calibration_reference = capture_module_outputs(model, tokenizer, modules, fixture["calibration"], device)
    baseline = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device=device)
    variants = []
    tensors = {}
    calibration_records = {}
    for variant_id, profile, ideal in (
        ("ideal_tiled_control", Profile(), True),
        ("dac10_weight8_adc12", Profile(adc_bits=12), False),
    ):
        print(f"Evaluating {variant_id} across {len(modules)} modules", flush=True)
        projections = {
            name: TiledProjection(module.weight, module.bias, bounds[name], profile, fixture["seed"])
            for name, module in modules.items()
        }
        replacements = [(module, (lambda x, projection=projections[name]: projection(x, ideal=ideal)))
                        for name, module in modules.items()]
        if not ideal:
            with replace_forwards(replacements):
                calibration_candidate = capture_module_outputs(model, tokenizer, modules, fixture["calibration"], device)
            for name, projection in projections.items():
                scale, correction = affine_fit(calibration_reference[name], calibration_candidate[name])
                projection.output_scale = scale
                projection.output_correction = correction
                delta_before = calibration_candidate[name].double() - calibration_reference[name].double()
                calibrated_values = calibration_candidate[name].double() * scale.double() + correction.double()
                calibration_records[name] = {
                    "method": "per-output-channel affine gain and offset correction",
                    "rows": int(calibration_reference[name].shape[0]),
                    "channels": int(calibration_reference[name].shape[1]),
                    "relative_l2_before": float(torch.linalg.vector_norm(delta_before) / torch.linalg.vector_norm(calibration_reference[name].double()).clamp_min(1e-12)),
                    "relative_l2_after": float(torch.linalg.vector_norm(calibrated_values - calibration_reference[name].double()) / torch.linalg.vector_norm(calibration_reference[name].double()).clamp_min(1e-12)),
                    "scale_min": float(scale.min()),
                    "scale_max": float(scale.max()),
                }
            for projection in projections.values():
                clear_projection(projection)
        with replace_forwards(replacements):
            uncalibrated_candidate = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device=device)
        uncalibrated_quality = compare(baseline, uncalibrated_candidate)
        uncalibrated_values = {name: flatten_outputs(projection).copy() for name, projection in projections.items()}
        uncalibrated_traces = {name: list(projection.trace) for name, projection in projections.items()}
        if not ideal:
            for projection in projections.values():
                clear_projection(projection)
            with replace_forwards(replacements):
                candidate = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device=device)
            quality = compare(baseline, candidate)
        else:
            candidate = uncalibrated_candidate
            quality = uncalibrated_quality
        screen = fixture["exploratory_screen"]
        module_records = {}
        for name, projection in projections.items():
            module_key = name.replace(".", "__")
            values = flatten_outputs(projection)
            if ideal:
                tensors[f"{module_key}__{variant_id}"] = values
            else:
                tensors[f"{module_key}__{variant_id}__uncalibrated"] = uncalibrated_values[name]
                tensors[f"{module_key}__{variant_id}__calibrated"] = values
            module_records[name] = {
                "weight_shape_input_output": list(projection.weight.shape),
                "activation_bound": bounds[name],
                "output_vector_count": int(values.shape[0]),
                "output_channel_count": int(values.shape[1]),
                "contract": projection.contract(),
                "trace": projection.trace,
                "uncalibrated_trace": uncalibrated_traces[name],
                "tensor_artifact_key": f"{module_key}__{variant_id}" if ideal else f"{module_key}__{variant_id}__calibrated",
                "uncalibrated_tensor_artifact_key": None if ideal else f"{module_key}__{variant_id}__uncalibrated",
                "calibration": None if ideal else calibration_records[name],
                "claim_boundary": "Per-module local tensor replay; not physical hardware output.",
            }
        variants.append({
            "id": variant_id,
            "quality": quality,
            "uncalibrated_quality": None if ideal else uncalibrated_quality,
            "exploratory_quality_screen_pass": quality["nll_increase_nats"] <= screen["maximum_nll_increase_nats"]
                                                and quality["teacher_forced_argmax_agreement"] >= screen["minimum_teacher_forced_argmax_agreement"],
            "modules": module_records,
        })
    if not all(row["maximum_logit_abs_error"] < 1e-3 and row["generation_exact_match"]
               for row in variants[0]["quality"]["rows"]):
        raise RuntimeError("ideal multi-module control failed")
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    tensor_path = output / "projection_tensors.npz"
    np.savez_compressed(tensor_path, **tensors)
    report = {
        "schema_version": "gpt2-multimodule-replay-v0.1",
        "result_type": "local_multi_module_profile_replay",
        "evidence_kind": "real_pretrained_model_with_provisional_numerical_array_on_cpu",
        "sources": {"fixture": source(args.fixture), "runner": source(Path(__file__)),
                    "projection_model": source(Path(__file__).with_name("tiled_projection_model.py")),
                    "model_snapshot": [source(path) for path in sorted(snapshot.iterdir()) if path.is_file()],
                    "projection_tensor_artifact": source(tensor_path)},
        "model": {"id": fixture["model_id"], "revision": fixture["revision"],
                  "target_modules": fixture["target_modules"], "parameter_count": sum(p.numel() for p in model.parameters())},
        "runtime": {"python": sys.version, "torch": torch.__version__, "transformers": transformers.__version__,
                    "platform": platform.platform(), "device": str(device), "threads": args.threads, "command": sys.argv},
        "fixture": fixture,
        "activation_bounds": bounds,
        "calibration": calibration_records,
        "variants": variants,
        "decision": "multi_module_hybrid_benefit_unproven",
        "analog_authorized": False,
        "claim_boundary": fixture["claim_boundary"],
    }
    report_path = output / "multimodule_evaluation.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (output / "manifest.json").write_text(json.dumps({"files": [source(report_path), source(tensor_path)]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "modules": len(modules),
                      "variants": len(variants), "decision": report["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
