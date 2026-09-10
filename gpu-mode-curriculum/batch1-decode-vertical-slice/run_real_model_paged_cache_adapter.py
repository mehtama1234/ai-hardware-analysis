#!/usr/bin/env python3
"""Functional page-backed KV adapter test for real GPT-2 on CUDA.

The adapter deliberately gathers pages into the Transformers Cache interface
before attention. This proves model/cache integration and measures its current
copy overhead; it is not yet a fused paged-attention kernel.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache

ROOT = Path(__file__).resolve().parents[1]
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
if not SERVING.exists():
    SERVING = ROOT.parent / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
from paged_cache import PagedKVCache  # noqa: E402


REPORT = Path(__file__).resolve().parent / "reports" / "real-model-paged-cache-adapter.json"
MODEL_ID = "openai-community/gpt2"
PROMPTS = ("The system bottleneck is", "context movement " * 32 + " because", "context movement " * 128 + " because")
PAGE_SIZE = 16
MAX_NEW_TOKENS = 8
REPEATS = 3


def synced(fn):
    torch.cuda.synchronize()
    start = time.perf_counter_ns()
    value = fn()
    torch.cuda.synchronize()
    return (time.perf_counter_ns() - start) / 1e6, value


def pack_cache(cache, model):
    pages = []
    for layer in cache.layers:
        key = layer.keys[0]
        value = layer.values[0]
        page_cache = PagedKVCache(
            capacity_pages=(key.shape[1] + PAGE_SIZE - 1) // PAGE_SIZE,
            page_size=PAGE_SIZE,
            heads=key.shape[0],
            head_dim=key.shape[2],
            dtype=key.dtype,
            device=key.device,
        )
        handle = page_cache.allocate()
        page_cache.append(handle, key, value)
        pages.append((page_cache, handle))
    return pages


def restore_cache(pages, model):
    cache = DynamicCache(config=model.config)
    for index, (page_cache, handle) in enumerate(pages):
        key, value = page_cache.gather(handle)
        cache.update(key.unsqueeze(0), value.unsqueeze(0), index)
    return cache


def decode_normal(model, encoded):
    mask = encoded["attention_mask"]
    with torch.inference_mode():
        cache = DynamicCache(config=model.config)
        out = model(input_ids=encoded["input_ids"], attention_mask=mask, past_key_values=cache, use_cache=True)
        tokens = [out.logits[:, -1, :].argmax(dim=-1)]
        for _ in range(MAX_NEW_TOKENS - 1):
            mask = torch.cat((mask, mask.new_ones((1, 1))), dim=1)
            out = model(input_ids=tokens[-1].unsqueeze(-1), attention_mask=mask, past_key_values=out.past_key_values, use_cache=True)
            tokens.append(out.logits[:, -1, :].argmax(dim=-1))
    return torch.stack(tokens, dim=1)


def decode_paged(model, encoded):
    mask = encoded["attention_mask"]
    with torch.inference_mode():
        cache = DynamicCache(config=model.config)
        out = model(input_ids=encoded["input_ids"], attention_mask=mask, past_key_values=cache, use_cache=True)
        pages = pack_cache(out.past_key_values, model)
        tokens = [out.logits[:, -1, :].argmax(dim=-1)]
        for _ in range(MAX_NEW_TOKENS - 1):
            mask = torch.cat((mask, mask.new_ones((1, 1))), dim=1)
            restored = restore_cache(pages, model)
            out = model(input_ids=tokens[-1].unsqueeze(-1), attention_mask=mask, past_key_values=restored, use_cache=True)
            pages = pack_cache(out.past_key_values, model)
            tokens.append(out.logits[:, -1, :].argmax(dim=-1))
    return torch.stack(tokens, dim=1), pages


def measure(model, tokenizer):
    rows = []
    for prompt in PROMPTS:
        encoded = tokenizer([prompt], return_tensors="pt").to("cuda")
        synced(lambda: decode_normal(model, encoded))
        synced(lambda: decode_paged(model, encoded))
        normal_samples, paged_samples = [], []
        parity = True
        for _ in range(REPEATS):
            normal_ms, normal = synced(lambda: decode_normal(model, encoded))
            paged_ms, paged_result = synced(lambda: decode_paged(model, encoded))
            paged, _ = paged_result
            normal_samples.append(normal_ms)
            paged_samples.append(paged_ms)
            parity = parity and torch.equal(normal, paged)
        rows.append({
            "prompt_token_count": int(encoded["attention_mask"].sum().item()),
            "output_parity": parity,
            "normal_dynamic_cache_ms_median": statistics.median(normal_samples),
            "paged_adapter_ms_median": statistics.median(paged_samples),
            "paged_adapter_overhead_ratio": statistics.median(paged_samples) / max(statistics.median(normal_samples), 1e-12),
        })
    return rows


def main() -> int:
    if not torch.cuda.is_available():
        raise SystemExit("CUDA device required; run this entrypoint in Google Colab")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, use_safetensors=True).to("cuda").eval()
    rows = measure(model, tokenizer)
    report = {
        "schema_version": "real-model-paged-cache-adapter-v0.1",
        "experiment": "real_model_dynamic_cache_vs_page_backed_cache_adapter",
        "evidence_kind": "measured_gpu",
        "gpu_execution_accepted": True,
        "model_profile": {"model_id": MODEL_ID, "model_revision": getattr(model.config, "_commit_hash", None), "tokenizer_id": MODEL_ID, "trained": True, "parameter_count": sum(parameter.numel() for parameter in model.parameters())},
        "device": "cuda",
        "device_name": torch.cuda.get_device_name(0),
        "runtime": {"torch_version": torch.__version__, "transformers_version": __import__("transformers").__version__},
        "protocol": {"prompts": list(PROMPTS), "page_size_tokens": PAGE_SIZE, "max_new_tokens": MAX_NEW_TOKENS, "repeats": REPEATS, "timing": "CUDA synchronized around complete decode", "adapter": "pack pages, gather into DynamicCache, run attention, repack each step"},
        "rows": rows,
        "decision": "paged_cache_functionally_accepted_overhead_requires_fused_kernel" if all(row["output_parity"] for row in rows) else "paged_cache_rejected_for_output_mismatch",
        "claim_boundary": {"allowed": "Functional page-backed KV adapter parity and measured gather/repack overhead for this GPT-2/T4 scope.", "refused": "Fused paged-attention performance, eviction policy, production serving, energy savings, analog benefit, or silicon performance."},
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "output": str(REPORT), "device": report["device_name"], "parity": all(row["output_parity"] for row in rows), "decision": report["decision"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
