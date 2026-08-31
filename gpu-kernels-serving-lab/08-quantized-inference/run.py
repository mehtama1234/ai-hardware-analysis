"""Session 08: measure simple quantization drift and memory savings."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


HERE = Path(__file__).resolve().parent
MODEL_ID = "hf-internal-testing/tiny-random-gpt2"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel_err(torch: Any, x: Any, q: Any) -> float:
    return float((x - q).norm() / (x.norm() + 1e-12))


def cosine(torch: Any, x: Any, q: Any) -> float:
    return float(torch.nn.functional.cosine_similarity(x.flatten(), q.flatten(), dim=0))


def int8_quant(torch: Any, x: Any) -> Any:
    scale = x.abs().max() / 127.0 + 1e-12
    return (x / scale).round().clamp(-127, 127) * scale


def int4_block_quant(torch: Any, x: Any, block: int = 32) -> Any:
    flat = x.flatten()
    flat = flat[: (flat.numel() // block) * block]
    view = flat.view(-1, block)
    scale = view.abs().amax(-1, keepdim=True) / 7.0 + 1e-12
    return ((view / scale).round().clamp(-7, 7) * scale).flatten()


def mxfp4_like_quant(torch: Any, x: Any, block: int = 32) -> Any:
    codes = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0], dtype=x.dtype, device=x.device)
    flat = x.flatten()
    flat = flat[: (flat.numel() // block) * block]
    view = flat.view(-1, block)
    scale = torch.pow(2.0, torch.ceil(torch.log2(view.abs().amax(-1, keepdim=True) / 6.0 + 1e-12)))
    scaled = view / scale
    idx = (scaled.abs().unsqueeze(-1) - codes).abs().argmin(-1)
    return scaled.sign() * codes[idx] * scale


def load_weight_vector(torch: Any) -> tuple[str, Any, str | None]:
    try:
        from transformers import AutoModelForCausalLM  # type: ignore

        model = AutoModelForCausalLM.from_pretrained(MODEL_ID, use_safetensors=True)
        chunks = []
        for p in model.parameters():
            if p.is_floating_point():
                chunks.append(p.detach().float().flatten().cpu())
            if sum(c.numel() for c in chunks) >= 1_000_000:
                break
        return MODEL_ID, torch.cat(chunks)[:1_000_000], None
    except Exception as exc:
        torch.manual_seed(0)
        return "synthetic-lognormal-weights", torch.randn(1_000_000).float() * 0.02, repr(exc)


def main() -> None:
    import torch  # type: ignore

    start = time.perf_counter()
    source, weights, fallback_reason = load_weight_vector(torch)
    load_seconds = time.perf_counter() - start
    base = weights.flatten()
    q_int8 = int8_quant(torch, base)
    q_int4 = int4_block_quant(torch, base)
    base4 = base[: q_int4.numel()]
    q_mxfp4 = mxfp4_like_quant(torch, base)
    base_mx = base[: q_mxfp4.numel()]
    schemes = [
        ("fp16", 16.0, base.half().float(), base),
        ("int8", 8.0, q_int8, base),
        ("int4_block", 4.25, q_int4, base4),
        ("mxfp4_like", 4.25, q_mxfp4.flatten(), base_mx),
    ]
    rows = []
    for name, bits, q, ref in schemes:
        rows.append(
            {
                "scheme": name,
                "bits_per_param": bits,
                "values": int(q.numel()),
                "memory_mb": round(q.numel() * bits / 8 / 1e6, 4),
                "relative_error_pct": round(rel_err(torch, ref, q) * 100, 4),
                "cosine": round(cosine(torch, ref, q), 6),
            }
        )

    out = {
        "session": "08-quantized-inference",
        "timestamp": now(),
        "inventory": collect_inventory("08-quantized-inference"),
        "source": source,
        "fallback_reason": fallback_reason,
        "load_seconds": round(load_seconds, 3),
        "rows": rows,
        "boundary": (
            "This quantizes stored weights and measures numerical drift. It does not run a "
            "bitsandbytes CUDA kernel or prove end-task model quality."
        ),
    }
    path = HERE / "out_quantized_inference.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, source)
    for row in rows:
        print(row["scheme"], row["memory_mb"], "MB", row["relative_error_pct"], "% error")


if __name__ == "__main__":
    main()

