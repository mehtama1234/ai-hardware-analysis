"""Session 13: aggregate current artifacts into an end-to-end serving diagnosis."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.gpu_info import collect_inventory


HERE = Path(__file__).resolve().parent


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> None:
    artifacts = {
        "hf": load("01-hf-baseline/out_hf_baseline.json"),
        "roofline": load("02-roofline/out_roofline.json"),
        "cuda": load("03-cuda-vector-reduce/out_cuda_vector_reduce.json"),
        "cuda_matmul": load("04-cuda-tiled-matmul/out_cuda_tiled_matmul.json"),
        "attention": load("05-cuda-tiny-attention/out_cuda_tiny_attention.json"),
        "triton": load("06-triton-matmul/out_triton_matmul.json"),
        "triton_attention": load("07-triton-fused-attention/out_triton_fused_attention.json"),
        "quant": load("08-quantized-inference/out_quantized_inference.json"),
        "vllm": load("09-vllm-serving/out_vllm_serving.json"),
        "kv": load("10-kv-cache-memory-manager/out_kv_cache_memory_manager.json"),
        "hip": load("11-rocm-hip-port/out_rocm_hip_port.json"),
        "jax": load("12-jax-scaling-practicum/out_jax_scaling.json"),
        "load_test": load("13-capstone-mini-serving-engine/out_load_test.json"),
    }
    hf = artifacts["hf"]["result"]
    vllm = artifacts["vllm"]["result"]
    load_test = artifacts["load_test"]
    serving_paths = load_test["paths"]
    high_level = serving_paths["high_level_single_request"]
    optimized = serving_paths["optimized_batched_prefix_cache"]
    blocked = []
    for name in ["cuda", "cuda_matmul", "triton", "triton_attention", "vllm", "hip"]:
        status = artifacts[name]["result"]["status"]
        if status != "ran" and status != "ready":
            blocked.append({"area": name, "status": status, "reason": artifacts[name]["result"].get("reason")})
    kv_rows = artifacts["kv"]["rows"]
    diagnosis = {
        "current_serving_path": hf["path"],
        "device": hf["device"],
        "tokens_per_sec": hf["tokens_per_sec"],
        "serving_path_comparison": {
            "high_level": {
                "name": "single-request local endpoint",
                "endpoint": high_level["endpoint"],
                "backend": high_level["backend"],
                "tokens_per_sec": high_level["tokens_per_sec"],
                "latency_ms_total": high_level["latency_ms"]["total"],
            },
            "optimized": {
                "name": "batched prefix-cache local endpoint",
                "endpoint": optimized["endpoint"],
                "backend": optimized["backend"],
                "tokens_per_sec": optimized["tokens_per_sec"],
                "latency_ms_total": optimized["latency_ms"]["total"],
                "prefix_tokens_reused": optimized["prefix_tokens_reused"],
            },
            "optimized_latency_speedup": load_test["comparison"]["optimized_latency_speedup"],
        },
        "main_bottleneck_now": (
            "environment/runtime availability before GPU optimization"
            if blocked
            else "ready for optimized serving comparison"
        ),
        "strongest_measured_signal": "HF baseline runs; the capstone compares single-request serving with a batched prefix-cache path; roofline and quantization produce local measurements; KV-cache simulator shows prefix reuse can decide whether batches fit.",
        "next_optimization": (
            "Expose CUDA/nvcc and install vLLM/bitsandbytes in that GPU environment, then rerun Sessions 03, 06, 08, and 09."
            if blocked
            else "Run vLLM load generation and compare against Session 01 plus the capstone endpoint."
        ),
        "kv_cache_pressure_case": max(kv_rows, key=lambda r: r["blocks_with_prefix_cache"]),
        "blocked": blocked,
    }
    out = {
        "session": "13-capstone-mini-serving-engine",
        "timestamp": now(),
        "inventory": collect_inventory("13-capstone-mini-serving-engine"),
        "artifacts_used": list(artifacts.keys()),
        "diagnosis": diagnosis,
        "boundary": (
            "This capstone currently aggregates measured tutorial artifacts into a serving diagnosis. "
            "It also runs two minimal HTTP completion paths: single-request high-level serving and "
            "batched prefix-cache serving. Optimized GPU serving still depends on a CUDA/ROCm "
            "environment with vLLM or equivalent runtime support."
        ),
    }
    path = HERE / "out_capstone_report.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name)
    print(diagnosis["main_bottleneck_now"])


if __name__ == "__main__":
    main()
