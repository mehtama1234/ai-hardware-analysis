"""Session 06: Triton blocked matmul benchmark, with no-GPU skip behavior."""

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

    result: dict[str, object]
    if not torch.cuda.is_available():
        result = {
            "status": "skipped",
            "reason": "Triton GPU kernels require a CUDA-visible device in this tutorial slice.",
            "boundary": (
                "Triton is installed, but no CUDA device is visible to PyTorch. The tutorial "
                "page documents the blocked state instead of pretending a kernel ran."
            ),
        }
    else:
        import triton  # type: ignore
        import triton.language as tl  # type: ignore

        @triton.jit
        def matmul_kernel(a, b, c, n: tl.constexpr, block: tl.constexpr):
            pid_m = tl.program_id(0)
            pid_n = tl.program_id(1)
            offs_m = pid_m * block + tl.arange(0, block)
            offs_n = pid_n * block + tl.arange(0, block)
            offs_k = tl.arange(0, block)
            acc = tl.zeros((block, block), tl.float32)
            for k0 in range(0, n, block):
                k = k0 + offs_k
                av = tl.load(a + offs_m[:, None] * n + k[None, :], mask=(offs_m[:, None] < n) & (k[None, :] < n), other=0.0)
                bv = tl.load(b + k[:, None] * n + offs_n[None, :], mask=(k[:, None] < n) & (offs_n[None, :] < n), other=0.0)
                acc += tl.dot(av, bv)
            tl.store(c + offs_m[:, None] * n + offs_n[None, :], acc, mask=(offs_m[:, None] < n) & (offs_n[None, :] < n))

        n, block = 1024, 32
        a = torch.randn((n, n), device="cuda", dtype=torch.float16)
        b = torch.randn((n, n), device="cuda", dtype=torch.float16)
        c = torch.empty((n, n), device="cuda", dtype=torch.float16)
        grid = (triton.cdiv(n, block), triton.cdiv(n, block))
        matmul_kernel[grid](a, b, c, n, block)
        torch.cuda.synchronize()
        start = time.perf_counter()
        for _ in range(20):
            matmul_kernel[grid](a, b, c, n, block)
        torch.cuda.synchronize()
        triton_ms = (time.perf_counter() - start) * 1000 / 20
        start = time.perf_counter()
        for _ in range(20):
            ref = a @ b
        torch.cuda.synchronize()
        torch_ms = (time.perf_counter() - start) * 1000 / 20
        err = (c.float() - ref.float()).abs().max().item()
        flops = 2 * n * n * n
        result = {
            "status": "ran",
            "n": n,
            "block": block,
            "triton_ms": round(triton_ms, 4),
            "torch_ms": round(torch_ms, 4),
            "triton_tflops": round(flops / (triton_ms / 1000) / 1e12, 4),
            "torch_tflops": round(flops / (torch_ms / 1000) / 1e12, 4),
            "max_abs_error": round(err, 6),
            "boundary": (
                "This is a readable blocked matmul tutorial kernel. It is not tuned to beat cuBLAS."
            ),
        }

    out = {
        "session": "06-triton-matmul",
        "timestamp": now(),
        "inventory": collect_inventory("06-triton-matmul"),
        "result": result,
    }
    path = HERE / "out_triton_matmul.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, result["status"])


if __name__ == "__main__":
    main()

