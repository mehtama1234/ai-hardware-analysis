#!/usr/bin/env python3
"""Compare cached and uncached generation for a real pretrained causal LM."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def measure(model, tokenizer, prompt: str, device: str, max_new_tokens: int, use_cache: bool, repeats: int) -> dict:
    encoded = tokenizer(prompt, return_tensors="pt")
    encoded = {key: value.to(device) for key, value in encoded.items()}
    samples = []
    output_ids = None
    for _ in range(repeats):
        if device == "cuda":
            torch.cuda.synchronize()
        start = time.perf_counter_ns()
        with torch.inference_mode():
            generated = model.generate(**encoded, max_new_tokens=max_new_tokens, do_sample=False, use_cache=use_cache)
        if device == "cuda":
            torch.cuda.synchronize()
        samples.append((time.perf_counter_ns() - start) / 1e6)
        output_ids = generated[0].detach().cpu().tolist()
    prompt_tokens = int(encoded["input_ids"].shape[-1])
    return {
        "use_cache": use_cache,
        "prompt_token_count": prompt_tokens,
        "generated_token_count": len(output_ids) - prompt_tokens,
        "output_token_ids": output_ids,
        "output_text": tokenizer.decode(output_ids, skip_special_tokens=False),
        "wall_time_ms_samples": samples,
        "wall_time_ms_median": statistics.median(samples),
        "wall_time_ms_p95": max(samples),
        "scope": "end_to_end_prefill_plus_decode; not separate phase timing",
    }


def run(model_id: str, prompts: list[str], requested_device: str, max_new_tokens: int, repeats: int, seed: int) -> dict:
    torch.manual_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, use_safetensors=True)
    device = requested_device if requested_device != "cuda" or torch.cuda.is_available() else "cpu"
    model.to(device).eval()
    rows = []
    for prompt in prompts:
        cached = measure(model, tokenizer, prompt, device, max_new_tokens, True, repeats)
        uncached = measure(model, tokenizer, prompt, device, max_new_tokens, False, repeats)
        rows.append({
            "prompt": prompt,
            "cached": cached,
            "uncached": uncached,
            "output_parity": cached["output_token_ids"] == uncached["output_token_ids"],
            "cache_speedup_ratio": uncached["wall_time_ms_median"] / max(cached["wall_time_ms_median"], 1e-12),
        })
    return {
        "schema_version": "real-model-serving-comparison-v0.1",
        "experiment": "real_model_cached_vs_uncached_generation",
        "evidence_kind": "measured_gpu" if device == "cuda" else "measured_cpu",
        "gpu_execution_accepted": device == "cuda",
        "model_profile": {
            "model_id": model_id,
            "model_revision": getattr(model.config, "_commit_hash", None),
            "tokenizer_id": model_id,
            "tokenizer_revision": getattr(tokenizer, "init_kwargs", {}).get("_commit_hash"),
            "trained": True,
            "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        },
        "tokenizer": {"class": tokenizer.__class__.__name__, "vocab_size": len(tokenizer)},
        "device": device,
        "device_name": torch.cuda.get_device_name(0) if device == "cuda" else platform.processor() or platform.machine(),
        "runtime": {"torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__},
        "protocol": {"workloads": prompts, "max_new_tokens": max_new_tokens, "repeats": repeats, "seed": seed},
        "rows": rows,
        "claim_boundary": {
            "allowed": "Real pretrained model cached/uncached output parity and measured timing at the recorded device and scope.",
            "refused": "Separate prefill/decode attribution, measured energy, analog benefit, or production readiness without those measurements.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="openai-community/gpt2")
    parser.add_argument("--prompt", action="append", dest="prompts", default=[])
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--max-new-tokens", type=int, default=8)
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--seed", type=int, default=8181)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.prompts:
        args.prompts = ["The system bottleneck is"]
    result = run(args.model, args.prompts, args.device, args.max_new_tokens, args.repeats, args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "real_model_serving_comparison.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "evidence_kind": result["evidence_kind"], "device": result["device"], "parity": [row["output_parity"] for row in result["rows"]]}, indent=2))


if __name__ == "__main__":
    main()
