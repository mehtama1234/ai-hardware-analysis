#!/usr/bin/env python3
"""Prove per-vector digital fallback parity for the frozen three-module slice."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_gpt2_multimodule_replay import PINNED_REVISION


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_hash(row: torch.Tensor) -> str:
    return hashlib.sha256(row.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-path", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--expected-runtime-trace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    runtime = json.loads(args.expected_runtime_trace.read_text(encoding="utf-8"))
    if fixture["revision"] != PINNED_REVISION:
        raise SystemExit("fixture revision is not pinned")
    if runtime.get("workload_vectors") != 162:
        raise SystemExit("expected runtime trace is not the retained 162-vector schedule")
    texts = fixture.get("evaluation") or fixture.get("calibration")
    if not texts:
        raise SystemExit("fixture has no replay texts")
    torch.set_num_threads(args.threads)
    model = AutoModelForCausalLM.from_pretrained(args.snapshot_path, local_files_only=True,
                                                 use_safetensors=True, attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(args.snapshot_path, local_files_only=True)
    modules = {name: model.get_submodule(name) for name in fixture["target_modules"]}
    inputs = {name: [] for name in modules}
    outputs = {name: [] for name in modules}
    handles = []
    for name, module in modules.items():
        def before(_module, args_, module_name=name):
            inputs[module_name].append(args_[0].detach().cpu().reshape(-1, args_[0].shape[-1]))
        def after(_module, _args, result, module_name=name):
            if isinstance(result, tuple):
                result = result[0]
            outputs[module_name].append(result.detach().cpu().reshape(-1, result.shape[-1]))
        handles.extend((module.register_forward_pre_hook(before), module.register_forward_hook(after)))
    try:
        with torch.inference_mode():
            for text in texts:
                encoded = tokenizer(text, return_tensors="pt")
                model(**encoded, use_cache=False)
                model.generate(**encoded, max_new_tokens=fixture["max_new_tokens"],
                               do_sample=False, use_cache=True,
                               pad_token_id=tokenizer.eos_token_id)
    finally:
        for handle in handles:
            handle.remove()
    module_reports = {}
    for name, module in modules.items():
        native = torch.cat(outputs[name], dim=0)
        activation = torch.cat(inputs[name], dim=0).to(module.weight.dtype)
        # GPT-2 Conv1D uses torch.addmm(bias, activation, weight); retain that
        # kernel/order so the fallback comparison is against the actual native
        # digital implementation, not merely an algebraically equivalent GEMM.
        fallback = torch.addmm(module.bias.detach().cpu(), activation, module.weight.detach().cpu())
        if native.shape[0] != 162:
            raise SystemExit(f"{name} replay produced {native.shape[0]} vectors, expected 162")
        native_hashes = [row_hash(row) for row in native]
        fallback_hashes = [row_hash(row) for row in fallback]
        difference = (native - fallback).abs()
        equal = [left == right for left, right in zip(native_hashes, fallback_hashes)]
        numerical_equal = [bool(torch.allclose(left, right, atol=3e-5, rtol=1e-5))
                           for left, right in zip(native, fallback)]
        module_reports[name] = {"vectors": int(native.shape[0]), "output_width": int(native.shape[1]),
                                "mismatch_count": equal.count(False), "exact_match": all(equal),
                                "numerical_mismatch_count": numerical_equal.count(False),
                                "numerical_match_atol_3e-5_rtol_1e-5": all(numerical_equal),
                                "maximum_abs_error": float(difference.max()),
                                "native_row_sha256": native_hashes, "fallback_row_sha256": fallback_hashes}
    output = {
        "schema_version": "gpt2-transformer-per-vector-fallback-fingerprint-v0.1",
        "result_type": "local_transformer_per_vector_digital_fallback_fingerprint",
        "sources": {"fixture": {"path": str(args.fixture), "sha256": digest(args.fixture)},
                    "expected_runtime_trace": {"path": str(args.expected_runtime_trace), "sha256": digest(args.expected_runtime_trace)},
                    "runner": {"path": str(Path(__file__)), "sha256": digest(Path(__file__))}},
        "model_revision": PINNED_REVISION, "workload_vectors": 162,
        "target_modules": list(modules), "modules": module_reports,
        "all_modules_exact": all(row["exact_match"] for row in module_reports.values()),
        "all_modules_numerically_equal": all(row["numerical_match_atol_3e-5_rtol_1e-5"] for row in module_reports.values()),
        "total_mismatch_count": sum(row["mismatch_count"] for row in module_reports.values()),
        "analog_authorized": False,
        "claim_boundary": "Local CPU per-vector digital fallback recomputation and bitwise row fingerprints for the frozen module slice; no physical analog execution, measured hardware latency, energy, or silicon claim.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "per_vector_fallback_fingerprint.json"
    report_path.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        {"path": str(args.fixture), "sha256": digest(args.fixture)},
        {"path": str(args.expected_runtime_trace), "sha256": digest(args.expected_runtime_trace)},
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "workload_vectors": 162,
                      "all_modules_exact": output["all_modules_exact"], "total_mismatch_count": output["total_mismatch_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
