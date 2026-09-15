#!/usr/bin/env python3
"""Run a disjoint local GPT-2 projection calibration and held-out replay.

The correction is fitted only on fixture calibration texts.  It is a software
calibration experiment; it does not imply circuit calibration or hardware
authorization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_gpt2_hybrid_evaluation import compare, evaluate, replace_forward
from tiled_projection_model import Profile, TiledProjection


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "experiments/gpt2-hybrid-v1/fixture.json"
PINNED_REVISION = "607a30d783dfa663caf39e06633721c8d4cfcd7e"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture_outputs(model, tokenizer, module, texts, device):
    captured = []

    def hook(_module, _inputs, output):
        if isinstance(output, tuple):
            output = output[0]
        captured.append(output.detach().cpu().reshape(-1, output.shape[-1]))

    handle = module.register_forward_hook(hook)
    try:
        with torch.inference_mode():
            for text in texts:
                encoded = {key: value.to(device) for key, value in tokenizer(text, return_tensors="pt").items()}
                model(**encoded, use_cache=False)
    finally:
        handle.remove()
    return torch.cat(captured, dim=0)


def metrics(reference: torch.Tensor, candidate: torch.Tensor) -> dict[str, float]:
    delta = candidate.double() - reference.double()
    denominator = max(float(torch.linalg.vector_norm(reference.double())), 1e-12)
    return {
        "rows": int(reference.shape[0]),
        "channels": int(reference.shape[1]),
        "rmse": float(torch.sqrt(torch.mean(delta * delta))),
        "max_absolute_error": float(delta.abs().max()),
        "relative_l2_error": float(torch.linalg.vector_norm(delta) / denominator),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-path", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    if fixture["revision"] != PINNED_REVISION:
        raise SystemExit("fixture revision is not the pinned GPT-2 revision")
    torch.set_num_threads(args.threads)
    device = torch.device("cpu")
    model = AutoModelForCausalLM.from_pretrained(args.snapshot_path, local_files_only=True,
                                                  use_safetensors=True, attn_implementation="eager").to(device).eval()
    tokenizer = AutoTokenizer.from_pretrained(args.snapshot_path, local_files_only=True)
    module = model.get_submodule(fixture["target_module"])

    activation_bound = [0.0]
    def calibrate(_module, inputs):
        activation_bound[0] = max(activation_bound[0], float(inputs[0].abs().max()))
    handle = module.register_forward_pre_hook(calibrate)
    try:
        capture_outputs(model, tokenizer, module, fixture["calibration"], device)
    finally:
        handle.remove()

    calibration_reference = capture_outputs(model, tokenizer, module, fixture["calibration"], device)
    baseline = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device=device)
    projection = TiledProjection(module.weight, module.bias, activation_bound[0], Profile(adc_bits=12), fixture["seed"])
    with replace_forward(module, lambda x: projection(x, ideal=False)):
        calibration_uncalibrated = capture_outputs(model, tokenizer, module, fixture["calibration"], device)
        uncalibrated_calibration_rows = calibration_uncalibrated.shape[0]
        uncalibrated_output_start = sum(row.shape[0] for row in projection.output_vectors)
        uncalibrated_trace_start = len(projection.trace)
        uncalibrated = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], projection, device=device)
    uncalibrated_eval_rows = sum(row["vectors"] for row in projection.trace[uncalibrated_trace_start:])
    all_projection_outputs = torch.cat([torch.from_numpy(row) for row in projection.output_vectors], dim=0)
    uncalibrated_outputs = all_projection_outputs[uncalibrated_output_start:
                                                  uncalibrated_output_start + uncalibrated_eval_rows]
    reference_mean = calibration_reference.mean(dim=0)
    candidate_mean = calibration_uncalibrated.mean(dim=0)
    centered_reference = calibration_reference - reference_mean
    centered_candidate = calibration_uncalibrated - candidate_mean
    variance = (centered_candidate * centered_candidate).sum(dim=0).clamp_min(1e-12)
    scale = (centered_candidate * centered_reference).sum(dim=0) / variance
    correction = reference_mean - scale * candidate_mean
    projection.output_scale = scale
    projection.output_correction = correction
    with replace_forward(module, lambda x: projection(x, ideal=False)):
        calibration_calibrated = capture_outputs(model, tokenizer, module, fixture["calibration"], device)
        calibrated_output_start = sum(row.shape[0] for row in projection.output_vectors)
        calibrated_trace_start = len(projection.trace)
        calibrated = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], projection, device=device)
    calibrated_eval_rows = sum(row["vectors"] for row in projection.trace[calibrated_trace_start:])
    all_projection_outputs = torch.cat([torch.from_numpy(row) for row in projection.output_vectors], dim=0)
    calibrated_outputs = all_projection_outputs[calibrated_output_start:
                                                calibrated_output_start + calibrated_eval_rows]

    args.output.mkdir(parents=True, exist_ok=False)
    correction_path = args.output / "adc12_output_correction.npz"
    import numpy as np
    np.savez_compressed(correction_path, output_scale=scale.numpy(), output_correction=correction.numpy())
    tensor_path = args.output / "projection_tensors.npz"
    np.savez_compressed(tensor_path, adc12_uncalibrated=uncalibrated_outputs.numpy(),
                        adc12_calibrated=calibrated_outputs.numpy())
    report = {
        "schema_version": "gpt2-disjoint-projection-calibration-v0.1",
        "result_type": "local_gpt2_adc12_output_calibration_and_holdout_replay",
        "evidence_kind": "local_cpu_model_replay",
        "provenance": {
            "fixture": {"path": str(args.fixture), "sha256": sha256(args.fixture)},
            "snapshot": str(args.snapshot_path),
            "revision": fixture["revision"],
            "device": str(device),
            "threads": args.threads,
            "target_module": fixture["target_module"],
            "calibration_text_count": len(fixture["calibration"]),
            "evaluation_text_count": len(fixture["evaluation"]),
            "split_disjoint": not set(fixture["calibration"]) & set(fixture["evaluation"]),
        },
        "calibration": {
            "method": "per-output-channel affine gain and offset correction",
            "activation_bound": activation_bound[0],
            "correction_shape": list(correction.shape),
            "scale_shape": list(scale.shape),
            "correction_artifact": {"path": str(correction_path), "sha256": sha256(correction_path)},
            "projection_tensor_artifact": {"path": str(tensor_path), "sha256": sha256(tensor_path)},
            "uncalibrated_metrics": metrics(calibration_reference, calibration_uncalibrated),
            "calibrated_metrics": metrics(calibration_reference, calibration_calibrated),
        },
        "held_out": {
            "uncalibrated_quality": compare(baseline, uncalibrated),
            "calibrated_quality": compare(baseline, calibrated),
        },
        "decision": "calibration_candidate_requires_profile_and_timing_gates",
        "analog_authorized": False,
        "claim_boundary": "Disjoint local software calibration and GPT-2 holdout replay. This does not prove circuit calibration, measured hardware, energy, yield, or analog authorization.",
    }
    report_path = args.output / "calibration_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path),
                      "uncalibrated_holdout_nll_increase": report["held_out"]["uncalibrated_quality"]["nll_increase_nats"],
                      "calibrated_holdout_nll_increase": report["held_out"]["calibrated_quality"]["nll_increase_nats"],
                      "calibration_rmse_before": report["calibration"]["uncalibrated_metrics"]["rmse"],
                      "calibration_rmse_after": report["calibration"]["calibrated_metrics"]["rmse"]}, sort_keys=True))


if __name__ == "__main__":
    main()
