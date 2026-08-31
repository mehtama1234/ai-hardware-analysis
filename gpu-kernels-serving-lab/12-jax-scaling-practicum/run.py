"""Session 12: executable JAX scaling-book style estimates and jit timings."""

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
    result: dict[str, object]
    try:
        import jax  # type: ignore
        import jax.numpy as jnp  # type: ignore

        devices = [{"platform": d.platform, "kind": getattr(d, "device_kind", str(d))} for d in jax.devices()]
        n = 768
        key = jax.random.PRNGKey(0)
        a = jax.random.normal(key, (n, n), dtype=jnp.float32)
        b = jax.random.normal(key, (n, n), dtype=jnp.float32)

        def mm(x, y):
            return x @ y

        jitted = jax.jit(mm)
        start = time.perf_counter()
        out = jitted(a, b).block_until_ready()
        compile_plus_run_ms = (time.perf_counter() - start) * 1000
        start = time.perf_counter()
        out = jitted(a, b).block_until_ready()
        cached_run_ms = (time.perf_counter() - start) * 1000
        flops = 2 * n * n * n
        hidden, layers, seq, batch, dtype_bytes = 4096, 32, 8192, 1, 2
        kv_mb = batch * seq * layers * 2 * hidden * dtype_bytes / 1e6
        result = {
            "status": "ran",
            "jax_version": jax.__version__,
            "devices": devices,
            "matmul_n": n,
            "compile_plus_run_ms": round(compile_plus_run_ms, 3),
            "cached_run_ms": round(cached_run_ms, 3),
            "cached_tflops": round(flops / (cached_run_ms / 1000) / 1e12, 6),
            "sample_checksum": round(float(out[0, 0]), 6),
            "kv_cache_estimate": {
                "batch": batch,
                "sequence": seq,
                "layers": layers,
                "hidden": hidden,
                "dtype_bytes": dtype_bytes,
                "kv_cache_mb": round(kv_mb, 3),
            },
            "multi_device_status": "available" if len(devices) > 1 else "single-device-only",
            "boundary": (
                "This turns the scaling-book style cost model into a local JAX run and a KV-cache "
                "calculator. It does not demonstrate real multi-device sharding unless multiple "
                "JAX devices are visible."
            ),
        }
    except Exception as exc:
        result = {
            "status": "skipped",
            "reason": repr(exc),
            "boundary": "JAX is not importable or runnable in this environment.",
        }

    out = {
        "session": "12-jax-scaling-practicum",
        "timestamp": now(),
        "inventory": collect_inventory("12-jax-scaling-practicum"),
        "result": result,
    }
    path = HERE / "out_jax_scaling.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name, result["status"])


if __name__ == "__main__":
    main()

