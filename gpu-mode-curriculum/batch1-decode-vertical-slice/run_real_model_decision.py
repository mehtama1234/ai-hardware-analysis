#!/usr/bin/env python3
"""Run the real pretrained-model serving comparison on a Colab GPU."""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "reports" / "real-model-serving-comparison.json"
MODEL_ID = "openai-community/gpt2"
PROMPTS = (
    "The system bottleneck is",
    "Memory movement dominates transformer inference when context grows because",
    "attention cache attention cache attention cache attention cache",
)


def measure(model, tokenizer, prompt: str, use_cache: bool, repeats: int = 3) -> dict:
    encoded = tokenizer(prompt, return_tensors="pt").to("cuda")
    samples = []
    output_ids = None
    for _ in range(repeats):
        torch.cuda.synchronize()
        start = time.perf_counter_ns()
        with torch.inference_mode():
            generated = model.generate(**encoded, max_new_tokens=8, do_sample=False, use_cache=use_cache)
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


def main() -> int:
    if not torch.cuda.is_available():
        raise SystemExit("CUDA device required; this entrypoint is for Colab GPU runtimes")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, use_safetensors=True).to("cuda").eval()
    rows = []
    for prompt in PROMPTS:
        cached = measure(model, tokenizer, prompt, True)
        uncached = measure(model, tokenizer, prompt, False)
        rows.append({
            "prompt": prompt,
            "cached": cached,
            "uncached": uncached,
            "output_parity": cached["output_token_ids"] == uncached["output_token_ids"],
            "cache_speedup_ratio": uncached["wall_time_ms_median"] / max(cached["wall_time_ms_median"], 1e-12),
        })
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "schema_version": "real-model-serving-comparison-v0.1",
        "experiment": "real_model_cached_vs_uncached_generation",
        "evidence_kind": "measured_gpu",
        "gpu_execution_accepted": True,
        "model_profile": {
            "model_id": MODEL_ID,
            "model_revision": getattr(model.config, "_commit_hash", None),
            "tokenizer_id": MODEL_ID,
            "tokenizer_revision": getattr(tokenizer, "init_kwargs", {}).get("_commit_hash"),
            "trained": True,
            "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        },
        "tokenizer": {"class": tokenizer.__class__.__name__, "vocab_size": len(tokenizer)},
        "device": "cuda",
        "device_name": torch.cuda.get_device_name(0),
        "runtime": {"torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__},
        "protocol": {"workloads": list(PROMPTS), "max_new_tokens": 8, "repeats": 3, "generation": "greedy"},
        "rows": rows,
        "claim_boundary": {
            "allowed": "Real pretrained model cached/uncached output parity and measured CUDA timing at the recorded scope.",
            "refused": "Measured energy, analog benefit, or production readiness without synchronized power and hardware evidence.",
        },
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "output": str(REPORT), "device": torch.cuda.get_device_name(0), "parity": all(row["output_parity"] for row in rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
