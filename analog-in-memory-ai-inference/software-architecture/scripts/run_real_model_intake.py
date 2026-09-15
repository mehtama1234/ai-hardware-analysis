#!/usr/bin/env python3
"""Run a reproducible baseline intake for a real pretrained causal LM."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
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


def run(model_id: str, prompts: list[str], device: str, max_new_tokens: int, seed: int) -> dict:
    torch.manual_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, use_safetensors=True)
    resolved_device = device
    if device == "cuda" and not torch.cuda.is_available():
        resolved_device = "cpu"
    model = model.to(resolved_device).eval()
    rows = []
    for prompt in prompts:
        encoded = tokenizer(prompt, return_tensors="pt")
        encoded = {key: value.to(resolved_device) for key, value in encoded.items()}
        with torch.inference_mode():
            start = time.perf_counter_ns()
            generated = model.generate(**encoded, max_new_tokens=max_new_tokens, do_sample=False)
            elapsed_ms = (time.perf_counter_ns() - start) / 1e6
        output_ids = generated[0].detach().cpu().tolist()
        rows.append({
            "prompt": prompt,
            "prompt_token_count": int(encoded["input_ids"].shape[-1]),
            "output_token_count": len(output_ids) - int(encoded["input_ids"].shape[-1]),
            "output_token_ids": output_ids,
            "output_text": tokenizer.decode(output_ids, skip_special_tokens=False),
            "wall_time_ms": elapsed_ms,
        })
    return {
        "schema_version": "real-model-intake-v0.1",
        "evidence_kind": "measured_gpu" if resolved_device == "cuda" else "measured_cpu",
        "model_profile": {
            "model_id": model_id,
            "model_revision": getattr(model.config, "_commit_hash", None),
            "tokenizer_id": model_id,
            "tokenizer_revision": getattr(tokenizer, "init_kwargs", {}).get("_commit_hash"),
            "trained": True,
            "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        },
        "tokenizer": {
            "class": tokenizer.__class__.__name__,
            "vocab_size": len(tokenizer),
            "special_tokens_map": tokenizer.special_tokens_map,
        },
        "device": resolved_device,
        "device_name": torch.cuda.get_device_name(0) if resolved_device == "cuda" else platform.processor() or platform.machine(),
        "runtime": {"torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__},
        "protocol": {"prompts": prompts, "max_new_tokens": max_new_tokens, "seed": seed, "generation": "greedy"},
        "rows": rows,
        "claim_boundary": {
            "allowed": "Real pretrained model/tokenizer intake and baseline generation at the recorded evidence level.",
            "refused": "Candidate speedup, measured energy, analog benefit, or production readiness without paired candidate and synchronized measurements.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="HuggingFaceTB/SmolLM2-135M")
    parser.add_argument("--prompt", action="append", dest="prompts", default=["The system bottleneck is"])
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--max-new-tokens", type=int, default=12)
    parser.add_argument("--seed", type=int, default=8181)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.model, args.prompts, args.device, args.max_new_tokens, args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "real_model_intake.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "evidence_kind": result["evidence_kind"], "model": result["model_profile"]}, indent=2))


if __name__ == "__main__":
    main()
