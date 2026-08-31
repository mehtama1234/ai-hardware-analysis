"""Session 05: tiny attention measurements before custom CUDA fusion."""

from __future__ import annotations

import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


HERE = Path(__file__).resolve().parent


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sync(torch: Any, device: str) -> None:
    if device == "cuda":
        torch.cuda.synchronize()


def bench(torch: Any, device: str, fn: Callable[[], Any], repeat: int = 10, warmup: int = 3) -> float:
    for _ in range(warmup):
        fn()
    sync(torch, device)
    samples = []
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        sync(torch, device)
        samples.append(time.perf_counter() - start)
    samples.sort()
    return samples[len(samples) // 2]


def materialized_attention(torch: Any, q: Any, k: Any, v: Any) -> Any:
    d = q.shape[-1]
    scores = (q @ k.transpose(-2, -1)) / math.sqrt(d)
    mask = torch.triu(torch.ones(scores.shape[-2:], dtype=torch.bool, device=scores.device), 1)
    scores = scores.masked_fill(mask, float("-inf"))
    probs = torch.softmax(scores, dim=-1)
    return probs @ v


def main() -> None:
    import torch  # type: ignore
    import torch.nn.functional as F

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    torch.manual_seed(0)
    batch, heads, dhead = 1, 4 if device == "cpu" else 8, 64
    lengths = [128, 256, 512] if device == "cpu" else [512, 1024, 2048]
    rows = []
    for n in lengths:
        q = torch.randn(batch, heads, n, dhead, device=device, dtype=dtype)
        k = torch.randn(batch, heads, n, dhead, device=device, dtype=dtype)
        v = torch.randn(batch, heads, n, dhead, device=device, dtype=dtype)
        mat_sec = bench(torch, device, lambda: materialized_attention(torch, q, k, v), repeat=6)
        sdpa_sec = bench(torch, device, lambda: F.scaled_dot_product_attention(q, k, v, is_causal=True), repeat=6)
        out_mat = materialized_attention(torch, q, k, v)
        out_sdpa = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        max_err = float((out_mat - out_sdpa).abs().max())
        attention_matrix_mb = batch * heads * n * n * q.element_size() / 1e6
        rows.append(
            {
                "sequence": n,
                "materialized_ms": round(mat_sec * 1000, 3),
                "sdpa_ms": round(sdpa_sec * 1000, 3),
                "sdpa_speedup": round(mat_sec / sdpa_sec, 3) if sdpa_sec else None,
                "attention_matrix_mb": round(attention_matrix_mb, 3),
                "max_abs_error": round(max_err, 6),
            }
        )

    decode_rows = []
    for context in ([128, 512, 2048] if device == "cpu" else [1024, 4096, 16384]):
        q = torch.randn(batch, heads, 1, dhead, device=device, dtype=dtype)
        k = torch.randn(batch, heads, context, dhead, device=device, dtype=dtype)
        v = torch.randn(batch, heads, context, dhead, device=device, dtype=dtype)
        sec = bench(torch, device, lambda: F.scaled_dot_product_attention(q, k, v), repeat=10)
        kv_mb = 2 * batch * heads * context * dhead * q.element_size() / 1e6
        decode_rows.append(
            {
                "context": context,
                "decode_ms_per_token": round(sec * 1000, 4),
                "kv_cache_mb": round(kv_mb, 3),
            }
        )

    out = {
        "session": "05-cuda-tiny-attention",
        "timestamp": now(),
        "inventory": collect_inventory("05-cuda-tiny-attention"),
        "device": device,
        "dtype": str(dtype).replace("torch.", ""),
        "prefill_rows": rows,
        "decode_rows": decode_rows,
        "boundary": (
            "This is the PyTorch reference measurement for tiny attention. It exposes the "
            "materialization cost and KV-cache scaling that a later custom CUDA kernel must improve."
        ),
    }
    path = HERE / "out_cuda_tiny_attention.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, device)
    for row in rows:
        print("prefill", row["sequence"], row["materialized_ms"], "ms materialized", row["sdpa_ms"], "ms sdpa")
    for row in decode_rows:
        print("decode", row["context"], row["decode_ms_per_token"], "ms/token", row["kv_cache_mb"], "MB KV")


if __name__ == "__main__":
    main()

