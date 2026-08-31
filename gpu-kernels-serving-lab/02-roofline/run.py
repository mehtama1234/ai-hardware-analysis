"""Session 02: small roofline-style AI operation benchmarks."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sync(torch: Any, device: str) -> None:
    if device == "cuda":
        torch.cuda.synchronize()


def bench(torch: Any, device: str, fn: Callable[[], Any], repeat: int = 20, warmup: int = 5) -> float:
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


def main() -> None:
    import torch  # type: ignore

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    torch.manual_seed(0)
    rows = []

    n = 8_000_000 if device == "cuda" else 1_000_000
    a = torch.randn(n, device=device, dtype=dtype)
    b = torch.randn(n, device=device, dtype=dtype)
    sec = bench(torch, device, lambda: a + b)
    bytes_moved = 3 * a.element_size() * n
    rows.append(
        {
            "operation": "vector_add",
            "shape": [n],
            "seconds": round(sec, 6),
            "bytes_moved": bytes_moved,
            "flops": n,
            "effective_gbps": round(bytes_moved / sec / 1e9, 3),
            "effective_tflops": round(n / sec / 1e12, 6),
            "arithmetic_intensity_flop_per_byte": round(n / bytes_moved, 6),
            "classification": "memory-bound",
        }
    )

    nred = 4_000_000 if device == "cuda" else 1_000_000
    r = torch.randn(nred, device=device, dtype=dtype)
    sec = bench(torch, device, lambda: r.sum(), repeat=15)
    bytes_moved = r.element_size() * nred
    rows.append(
        {
            "operation": "reduction_sum",
            "shape": [nred],
            "seconds": round(sec, 6),
            "bytes_moved": bytes_moved,
            "flops": nred,
            "effective_gbps": round(bytes_moved / sec / 1e9, 3),
            "effective_tflops": round(nred / sec / 1e12, 6),
            "arithmetic_intensity_flop_per_byte": round(nred / bytes_moved, 6),
            "classification": "memory/synchronization-bound",
        }
    )

    m = 1024 if device == "cuda" else 512
    x = torch.randn(m, m, device=device, dtype=dtype)
    y = torch.randn(m, m, device=device, dtype=dtype)
    sec = bench(torch, device, lambda: x @ y, repeat=10)
    flops = 2 * m * m * m
    bytes_moved = 3 * x.element_size() * m * m
    rows.append(
        {
            "operation": "matmul",
            "shape": [m, m, m],
            "seconds": round(sec, 6),
            "bytes_moved": bytes_moved,
            "flops": flops,
            "effective_gbps": round(bytes_moved / sec / 1e9, 3),
            "effective_tflops": round(flops / sec / 1e12, 6),
            "arithmetic_intensity_flop_per_byte": round(flops / bytes_moved, 6),
            "classification": "compute-bound when large enough",
        }
    )

    heads, dhead, context = (16, 128, 16384) if device == "cuda" else (4, 64, 4096)
    k = torch.randn(heads, context, dhead, device=device, dtype=dtype)
    q = torch.randn(heads, dhead, device=device, dtype=dtype)
    sec = bench(torch, device, lambda: torch.einsum("hd,hld->hl", q, k), repeat=15)
    flops = 2 * heads * context * dhead
    bytes_moved = (k.numel() + q.numel() + heads * context) * k.element_size()
    rows.append(
        {
            "operation": "kv_cache_score_scan",
            "shape": [heads, context, dhead],
            "seconds": round(sec, 6),
            "bytes_moved": bytes_moved,
            "flops": flops,
            "effective_gbps": round(bytes_moved / sec / 1e9, 3),
            "effective_tflops": round(flops / sec / 1e12, 6),
            "arithmetic_intensity_flop_per_byte": round(flops / bytes_moved, 6),
            "classification": "memory-pressure attention primitive",
        }
    )

    out = {
        "session": "02-roofline",
        "timestamp": now(),
        "inventory": collect_inventory("02-roofline"),
        "device": device,
        "dtype": str(dtype).replace("torch.", ""),
        "rows": rows,
        "boundary": (
            "These are small microbenchmarks, useful for classifying operation shape. They are "
            "not vendor peak measurements and should not be compared to published peak specs."
        ),
    }
    path = Path(__file__).with_name("out_roofline.json")
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name)
    for row in rows:
        print(row["operation"], row["classification"], row["effective_gbps"], "GB/s", row["effective_tflops"], "TFLOP/s")


if __name__ == "__main__":
    main()

