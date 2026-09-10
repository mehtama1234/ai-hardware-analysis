#!/usr/bin/env python3
"""Measure real-model prefill/decode, KV-cache memory, and batch scaling on CUDA."""

from __future__ import annotations

import json
import statistics
import time
import argparse
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "reports" / "real-model-serving-characterization.json"
MODEL_ID = "openai-community/gpt2"
MODEL_REVISION = None
PROMPTS = (
    "The system bottleneck is",
    "Memory movement dominates transformer inference when context grows because",
    "attention cache attention cache attention cache attention cache",
    "A hardware decision must account for",
)
MAX_NEW_TOKENS = 8
REPEATS = 3


def clocked(fn):
    torch.cuda.synchronize()
    start = time.perf_counter_ns()
    value = fn()
    torch.cuda.synchronize()
    return (time.perf_counter_ns() - start) / 1e6, value


def generate_cached(model, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> tuple[torch.Tensor, float, float]:
    positions = attention_mask.long().cumsum(-1) - 1
    positions.masked_fill_(attention_mask == 0, 0)
    def prefill():
        with torch.inference_mode():
            return model(input_ids=input_ids, attention_mask=attention_mask,
                         position_ids=positions, use_cache=True)

    prefill_ms, out = clocked(prefill)
    past = out.past_key_values
    tokens = [out.logits[:, -1, :].argmax(dim=-1)]
    decode_mask = attention_mask

    def decode():
        nonlocal past, decode_mask
        with torch.inference_mode():
            for _ in range(MAX_NEW_TOKENS - 1):
                decode_mask = torch.cat((decode_mask, torch.ones((decode_mask.shape[0], 1), device=decode_mask.device, dtype=decode_mask.dtype)), dim=1)
                decode_positions = decode_mask.long().sum(-1, keepdim=True) - 1
                out = model(input_ids=tokens[-1].unsqueeze(-1), attention_mask=decode_mask,
                            position_ids=decode_positions, past_key_values=past, use_cache=True)
                past = out.past_key_values
                tokens.append(out.logits[:, -1, :].argmax(dim=-1))
            return torch.stack(tokens, dim=1)

    decode_ms, generated = clocked(decode)
    return generated, prefill_ms, decode_ms


def generate_uncached(model, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> tuple[torch.Tensor, float, float]:
    positions = attention_mask.long().cumsum(-1) - 1
    positions.masked_fill_(attention_mask == 0, 0)
    def prefill():
        with torch.inference_mode():
            return model(input_ids=input_ids, attention_mask=attention_mask,
                         position_ids=positions, use_cache=False)

    prefill_ms, out = clocked(prefill)
    sequence = torch.cat((input_ids, out.logits[:, -1, :].argmax(dim=-1, keepdim=True)), dim=1)
    decode_mask = torch.cat((attention_mask, torch.ones((attention_mask.shape[0], 1), device=attention_mask.device, dtype=attention_mask.dtype)), dim=1)

    def decode():
        nonlocal sequence, decode_mask
        with torch.inference_mode():
            for _ in range(MAX_NEW_TOKENS - 1):
                decode_positions = decode_mask.long().cumsum(-1) - 1
                decode_positions.masked_fill_(decode_mask == 0, 0)
                out = model(input_ids=sequence, attention_mask=decode_mask,
                            position_ids=decode_positions, use_cache=False)
                sequence = torch.cat((sequence, out.logits[:, -1, :].argmax(dim=-1, keepdim=True)), dim=1)
                decode_mask = torch.cat((decode_mask, torch.ones((decode_mask.shape[0], 1), device=decode_mask.device, dtype=decode_mask.dtype)), dim=1)
            return sequence[:, -MAX_NEW_TOKENS:]

    decode_ms, generated = clocked(decode)
    return generated, prefill_ms, decode_ms


def measure_batch(model, tokenizer, prompts: list[str], batch_size: int) -> dict:
    selected = prompts[:batch_size]
    encoded = tokenizer(selected, return_tensors="pt", padding=True, truncation=True).to("cuda")
    attention_mask = encoded["attention_mask"]
    input_ids = encoded["input_ids"]
    # Warm up both paths before recording allocator and timing samples.
    generate_cached(model, input_ids, attention_mask)
    generate_uncached(model, input_ids, attention_mask)
    cached_samples = []
    uncached_samples = []
    cached_peak = []
    uncached_peak = []
    parity = True
    for _ in range(REPEATS):
        torch.cuda.reset_peak_memory_stats()
        cached_tokens, cached_prefill_ms, cached_decode_ms = generate_cached(model, input_ids, attention_mask)
        cached_ms = cached_prefill_ms + cached_decode_ms
        cached_samples.append(cached_ms)
        cached_peak.append(torch.cuda.max_memory_allocated() / (1024 ** 2))
        torch.cuda.reset_peak_memory_stats()
        uncached_tokens, uncached_prefill_ms, uncached_decode_ms = generate_uncached(model, input_ids, attention_mask)
        uncached_ms = uncached_prefill_ms + uncached_decode_ms
        uncached_samples.append(uncached_ms)
        uncached_peak.append(torch.cuda.max_memory_allocated() / (1024 ** 2))
        parity = parity and torch.equal(cached_tokens, uncached_tokens)
    return {
        "batch_size": batch_size,
        "prompts": selected,
        "prompt_token_counts": attention_mask.sum(dim=1).detach().cpu().tolist(),
        "generated_token_count": MAX_NEW_TOKENS,
        "output_parity": parity,
        "cached": {
            "wall_time_ms_samples": cached_samples,
            "wall_time_ms_median": statistics.median(cached_samples),
            "wall_time_ms_p95": max(cached_samples),
            "peak_memory_mb_samples": cached_peak,
            "peak_memory_mb_max": max(cached_peak),
            "last_prefill_ms": cached_prefill_ms,
            "last_decode_ms": cached_decode_ms,
        },
        "uncached": {
            "wall_time_ms_samples": uncached_samples,
            "wall_time_ms_median": statistics.median(uncached_samples),
            "wall_time_ms_p95": max(uncached_samples),
            "peak_memory_mb_samples": uncached_peak,
            "peak_memory_mb_max": max(uncached_peak),
            "last_prefill_ms": uncached_prefill_ms,
            "last_decode_ms": uncached_decode_ms,
        },
        "cache_speedup_ratio_uncached_over_cached": statistics.median(uncached_samples) / max(statistics.median(cached_samples), 1e-12),
        "scope": "manual greedy prefill plus autoregressive decode; CUDA synchronized; allocator peak includes model and activations; phase fields are last measured repeat",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-id', default=MODEL_ID)
    parser.add_argument('--revision', default=MODEL_REVISION)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise SystemExit("CUDA device required; this entrypoint is for Colab GPU runtimes")
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, revision=args.revision)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(args.model_id, revision=args.revision, use_safetensors=True).to("cuda").eval()
    rows = [measure_batch(model, tokenizer, list(PROMPTS), size) for size in (1, 2, 4)]
    report = {
        "schema_version": "real-model-serving-characterization-v0.1",
        "experiment": "real_model_prefill_decode_kv_cache_batch_sweep",
        "evidence_kind": "measured_gpu",
        "gpu_execution_accepted": True,
        "model_profile": {
            "model_id": args.model_id,
            "model_revision": getattr(model.config, "_commit_hash", None),
            "tokenizer_id": args.model_id,
            "tokenizer_revision": getattr(tokenizer, "init_kwargs", {}).get("_commit_hash"),
            "trained": True,
            "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        },
        "device": "cuda",
        "device_name": torch.cuda.get_device_name(0),
        "runtime": {"torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__},
        "protocol": {"workloads": list(PROMPTS), "batch_sizes": [1, 2, 4], "max_new_tokens": MAX_NEW_TOKENS, "repeats": REPEATS, "generation": "greedy", "timing": "torch.cuda.synchronize before and after each sample"},
        "rows": rows,
        "claim_boundary": {
            "allowed": "Measured CUDA prefill-plus-decode cache comparison, allocator peaks, parity, and bounded batch scaling for this model and protocol.",
            "refused": "Energy, silicon/analog benefit, production capacity, or general cache superiority beyond this measured scope.",
        },
    }
    report['model_profile']['requested_revision'] = args.revision
    output = args.output or REPORT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "output": str(output), "device": report["device_name"], "rows": len(rows), "parity": all(row["output_parity"] for row in rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
