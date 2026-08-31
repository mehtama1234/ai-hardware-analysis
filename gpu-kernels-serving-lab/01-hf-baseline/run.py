"""Session 01: Hugging Face generation baseline with a deterministic fallback.

The preferred path uses a tiny real Transformers model so the benchmark exercises
tokenization, model loading, generation, and KV-cache behavior. If that path fails
because the model is not cached, network is unavailable, or a package mismatch
appears, a small local PyTorch causal model runs instead and records the fallback
boundary explicitly.
"""

from __future__ import annotations

import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


MODEL_ID = os.environ.get("GPU_LAB_HF_MODEL", "hf-internal-testing/tiny-random-gpt2")
PROMPTS = [
    "GPU kernels matter for language models because",
    "A KV cache is best understood as",
]
MAX_NEW_TOKENS = int(os.environ.get("GPU_LAB_MAX_NEW_TOKENS", "32"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def device_name(torch: Any) -> str:
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def memory_mb(torch: Any, device: str) -> float | None:
    if device == "cuda":
        return round(torch.cuda.max_memory_allocated() / 1e6, 3)
    try:
        import psutil  # type: ignore

        return round(psutil.Process().memory_info().rss / 1e6, 3)
    except Exception:
        return None


def estimate_kv_cache_mb(config: Any, prompt_tokens: int, batch_size: int, dtype_bytes: int) -> float | None:
    layers = getattr(config, "n_layer", None) or getattr(config, "num_hidden_layers", None)
    hidden = getattr(config, "n_embd", None) or getattr(config, "hidden_size", None)
    if not layers or not hidden:
        return None
    return round(batch_size * prompt_tokens * layers * 2 * hidden * dtype_bytes / 1e6, 4)


def run_hf() -> dict[str, Any]:
    import torch  # type: ignore
    from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore

    device = device_name(torch)
    dtype = torch.float16 if device == "cuda" else torch.float32
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()

    load_start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=dtype, use_safetensors=True)
    model.to(device)
    model.eval()
    load_seconds = time.perf_counter() - load_start

    encoded = tokenizer(PROMPTS, return_tensors="pt", padding=True)
    encoded = {k: v.to(device) for k, v in encoded.items()}
    prompt_tokens = int(encoded["input_ids"].shape[1])
    batch_size = int(encoded["input_ids"].shape[0])

    # TTFT is approximated by forcing one-token generation first.
    with torch.inference_mode():
        start = time.perf_counter()
        model.generate(**encoded, max_new_tokens=1, do_sample=False, pad_token_id=tokenizer.eos_token_id)
        if device == "cuda":
            torch.cuda.synchronize()
        ttft_ms = (time.perf_counter() - start) * 1000.0

        start = time.perf_counter()
        generated = model.generate(
            **encoded,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
        if device == "cuda":
            torch.cuda.synchronize()
        total_ms = (time.perf_counter() - start) * 1000.0

    generated_tokens = int(generated.shape[1] - prompt_tokens)
    total_new_tokens = generated_tokens * batch_size
    texts = tokenizer.batch_decode(generated[:, prompt_tokens:], skip_special_tokens=True)
    params = sum(p.numel() for p in model.parameters())
    dtype_bytes = 2 if dtype == torch.float16 else 4
    return {
        "path": "huggingface-transformers",
        "model": MODEL_ID,
        "device": device,
        "dtype": str(dtype).replace("torch.", ""),
        "batch_size": batch_size,
        "prompt_tokens": prompt_tokens,
        "generated_tokens_per_request": generated_tokens,
        "total_new_tokens": total_new_tokens,
        "load_seconds": round(load_seconds, 3),
        "ttft_ms": round(ttft_ms, 3),
        "total_decode_ms": round(total_ms, 3),
        "tokens_per_sec": round(total_new_tokens / (total_ms / 1000.0), 3) if total_ms else None,
        "peak_memory_mb": memory_mb(torch, device),
        "parameter_count": params,
        "weight_memory_mb_estimate": round(params * dtype_bytes / 1e6, 3),
        "kv_cache_mb_estimate": estimate_kv_cache_mb(model.config, prompt_tokens, batch_size, dtype_bytes),
        "sample_outputs": texts,
        "boundary": (
            "This is a high-level Transformers baseline. It measures end-to-end Python/model API "
            "generation on a tiny model, not optimized serving throughput or custom kernel speed."
        ),
    }


def run_fallback() -> dict[str, Any]:
    import torch  # type: ignore

    torch.manual_seed(0)
    device = device_name(torch)
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    vocab, hidden, layers, batch, prompt_tokens = 512, 128, 2, len(PROMPTS), 32
    emb = torch.nn.Embedding(vocab, hidden).to(device)
    blocks = torch.nn.ModuleList([torch.nn.Linear(hidden, hidden).to(device) for _ in range(layers)])
    head = torch.nn.Linear(hidden, vocab).to(device)
    tokens = torch.randint(0, vocab, (batch, prompt_tokens), device=device)
    params = sum(p.numel() for module in [emb, *blocks, head] for p in module.parameters())

    start = time.perf_counter()
    with torch.inference_mode():
        for _ in range(MAX_NEW_TOKENS):
            x = emb(tokens[:, -1])
            for block in blocks:
                x = torch.nn.functional.silu(block(x))
            logits = head(x)
            nxt = logits.argmax(-1, keepdim=True)
            tokens = torch.cat([tokens, nxt], dim=1)
    if device == "cuda":
        torch.cuda.synchronize()
    total_ms = (time.perf_counter() - start) * 1000.0
    total_new_tokens = batch * MAX_NEW_TOKENS
    return {
        "path": "local-pytorch-fallback",
        "model": "tiny-random-causal-mlp",
        "device": device,
        "dtype": "float32",
        "batch_size": batch,
        "prompt_tokens": prompt_tokens,
        "generated_tokens_per_request": MAX_NEW_TOKENS,
        "total_new_tokens": total_new_tokens,
        "load_seconds": 0.0,
        "ttft_ms": None,
        "total_decode_ms": round(total_ms, 3),
        "tokens_per_sec": round(total_new_tokens / (total_ms / 1000.0), 3) if total_ms else None,
        "peak_memory_mb": memory_mb(torch, device),
        "parameter_count": params,
        "weight_memory_mb_estimate": round(params * 4 / 1e6, 3),
        "kv_cache_mb_estimate": round(batch * prompt_tokens * layers * 2 * hidden * 4 / 1e6, 4),
        "sample_outputs": [],
        "boundary": (
            "Fallback ran because the real Hugging Face path failed. It proves the measurement "
            "harness works, but it is not a language-model serving result."
        ),
    }


def main() -> None:
    result: dict[str, Any]
    error: str | None = None
    try:
        result = run_hf()
    except Exception as exc:
        error = repr(exc)
        result = run_fallback()
        result["fallback_reason"] = error

    out = {
        "session": "01-hf-baseline",
        "timestamp": now(),
        "inventory": collect_inventory("01-hf-baseline"),
        "result": result,
    }
    path = Path(__file__).with_name("out_hf_baseline.json")
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name)
    print(result["path"], result["device"], result["tokens_per_sec"], "tokens/sec")
    if error:
        print("fallback_reason:", error)


if __name__ == "__main__":
    main()
