"""Session 07: Triton fused single-query attention, or skip without CUDA."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


HERE = Path(__file__).resolve().parent


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    import torch  # type: ignore

    if not torch.cuda.is_available():
        result = {
            "status": "skipped",
            "reason": "Triton fused-attention kernel requires a CUDA-visible device.",
            "boundary": (
                "The tutorial runner is present, but this environment cannot launch the Triton "
                "kernel until CUDA is visible."
            ),
        }
    else:
        import triton  # type: ignore
        import triton.language as tl  # type: ignore

        @triton.jit
        def decode_attention_kernel(q, k, v, out, context: tl.constexpr, d: tl.constexpr, block: tl.constexpr):
            offs_d = tl.arange(0, block)
            mask_d = offs_d < d
            qv = tl.load(q + offs_d, mask=mask_d, other=0.0).to(tl.float32)
            m = tl.full((), -3.4028234663852886e38, tl.float32)
            z = tl.full((), 0.0, tl.float32)
            acc = tl.zeros((block,), tl.float32)
            scale = 1.0 / tl.sqrt(d + 0.0)
            for t in range(0, context):
                kv = tl.load(k + t * d + offs_d, mask=mask_d, other=0.0).to(tl.float32)
                vv = tl.load(v + t * d + offs_d, mask=mask_d, other=0.0).to(tl.float32)
                score = tl.sum(qv * kv, axis=0) * scale
                m_new = tl.maximum(m, score)
                alpha = tl.exp(m - m_new)
                beta = tl.exp(score - m_new)
                acc = acc * alpha + vv * beta
                z = z * alpha + beta
                m = m_new
            tl.store(out + offs_d, acc / z, mask=mask_d)

        context, d, block = 2048, 64, 64
        q = torch.randn((d,), device="cuda", dtype=torch.float32)
        k = torch.randn((context, d), device="cuda", dtype=torch.float32)
        v = torch.randn((context, d), device="cuda", dtype=torch.float32)
        out = torch.empty((d,), device="cuda", dtype=torch.float32)
        decode_attention_kernel[(1,)](q, k, v, out, context, d, block)
        torch.cuda.synchronize()
        start = time.perf_counter()
        for _ in range(100):
            decode_attention_kernel[(1,)](q, k, v, out, context, d, block)
        torch.cuda.synchronize()
        triton_ms = (time.perf_counter() - start) * 1000 / 100
        start = time.perf_counter()
        for _ in range(100):
            ref = torch.nn.functional.scaled_dot_product_attention(
                q.view(1, 1, 1, d), k.view(1, 1, context, d), v.view(1, 1, context, d)
            ).view(d)
        torch.cuda.synchronize()
        torch_ms = (time.perf_counter() - start) * 1000 / 100
        err = float((out - ref).abs().max())
        bytes_read = (q.numel() + k.numel() + v.numel() + out.numel()) * q.element_size()
        result = {
            "status": "ran",
            "context": context,
            "d_head": d,
            "triton_ms": round(triton_ms, 4),
            "torch_sdpa_ms": round(torch_ms, 4),
            "speedup_vs_sdpa": round(torch_ms / triton_ms, 3) if triton_ms else None,
            "bytes_read_estimate": bytes_read,
            "max_abs_error": round(err, 6),
            "boundary": (
                "This is a single-query decode attention kernel that keeps online softmax state "
                "local. It is a tutorial stepping stone, not production FlashAttention."
            ),
        }

    out_doc = {"session": "07-triton-fused-attention", "timestamp": now(), "inventory": collect_inventory("07-triton-fused-attention"), "result": result}
    path = HERE / "out_triton_fused_attention.json"
    path.write_text(json.dumps(out_doc, indent=2), encoding="utf-8")
    print("wrote", path.name, result["status"])


if __name__ == "__main__":
    main()

