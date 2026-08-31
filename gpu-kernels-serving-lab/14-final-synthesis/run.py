"""Session 14: generate the final cross-session synthesis from measurement artifacts."""

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


def load_if_exists(rel: str) -> dict | None:
    path = ROOT / rel
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def corpus_bridge() -> dict:
    repo = ROOT.parent
    venue_pages = sorted(p.name for p in repo.glob("*-2025-bigpicture.html"))
    has_synthesis = (repo / "synthesis.html").exists()
    per_paper_count = len(list((repo / "analysis" / "per-paper").glob("*.json")))
    return {
        "top_level_synthesis": "synthesis.html" if has_synthesis else None,
        "venue_bigpicture_pages": venue_pages,
        "per_paper_json_count": per_paper_count,
        "interpretation": (
            "The lab turns the corpus-level hardware/software co-design themes into runnable exercises: "
            "MLSys-style serving software, ISCA/MICRO/HPCA-style memory and kernel bottlenecks, "
            "SC-style scaling and communication pressure, and Hot Chips/ISSCC-style deployment reality "
            "where availability, power, memory, and portability matter as much as a single kernel."
        ),
    }


def main() -> None:
    roofline = load("02-roofline/out_roofline.json")
    attention = load("05-cuda-tiny-attention/out_cuda_tiny_attention.json")
    quant = load("08-quantized-inference/out_quantized_inference.json")
    vllm = load("09-vllm-serving/out_vllm_serving.json")
    kv = load("10-kv-cache-memory-manager/out_kv_cache_memory_manager.json")
    jax = load("12-jax-scaling-practicum/out_jax_scaling.json")
    capstone = load("13-capstone-mini-serving-engine/out_capstone_report.json")
    gpumode_sources = [
        "15-gpumode-coalescing/out_gpumode_coalescing.json",
        "16-gpumode-warp-reductions/out_gpumode_warp_reductions.json",
        "17-gpumode-triton-autotune/out_gpumode_triton_autotune.json",
        "18-gpumode-online-softmax/out_gpumode_online_softmax.json",
        "19-gpumode-torch-compile/out_gpumode_torch_compile.json",
        "20-gpumode-vllm-scheduler/out_gpumode_vllm_scheduler.json",
        "21-gpumode-quantized-kernels/out_gpumode_quantized_kernels.json",
        "22-gpumode-nsight-roofline/out_gpumode_nsight_roofline.json",
        "23-gpumode-shared-memory-gemm/out_gpumode_shared_memory_gemm.json",
        "24-gpumode-tensor-core-cutlass/out_gpumode_tensor_core_cutlass.json",
        "25-gpumode-rocm-hip-portability/out_gpumode_rocm_hip_portability.json",
        "26-gpumode-distributed-communication/out_gpumode_distributed_communication.json",
    ]
    gpumode_artifacts = [artifact for rel in gpumode_sources if (artifact := load_if_exists(rel))]

    roof_rows = roofline["rows"]
    memory_rows = [row for row in roof_rows if "memory" in row["classification"]]
    compute_rows = [row for row in roof_rows if "compute" in row["classification"]]
    best_quant = min(quant["rows"], key=lambda row: row["memory_mb"])
    kv_best = max(kv["rows"], key=lambda row: row["saved_pct"])
    serving = capstone["diagnosis"]["serving_path_comparison"]
    blocked = capstone["diagnosis"]["blocked"]

    synthesis = {
        "scaling_book_language": {
            "compute": (
                f"{compute_rows[0]['operation']} is the clearest compute-shaped local benchmark "
                f"at arithmetic intensity {compute_rows[0]['arithmetic_intensity_flop_per_byte']} "
                f"FLOP/byte and {compute_rows[0]['effective_tflops']} TFLOP/s."
                if compute_rows
                else "No compute-shaped benchmark was identified in the current artifact set."
            ),
            "memory": (
                f"{memory_rows[0]['operation']} and KV-cache score scans expose memory pressure; "
                f"the KV-cache simulator shows {kv_best['saved_pct']}% block savings for "
                f"{kv_best['name']}."
                if memory_rows
                else "No memory-shaped benchmark was identified in the current artifact set."
            ),
            "communication": (
                f"JAX currently sees {len(jax['result']['devices'])} device(s), so the lab records "
                "single-device execution and treats cross-device communication as the next scaling layer."
            ),
        },
        "serving_language": {
            "kv_cache": f"Session 10 models block allocation and prefix reuse; the strongest case is {kv_best['name']}.",
            "batching": (
                "Session 13 compares single-request serving with a batched endpoint, showing "
                f"{serving['optimized_latency_speedup']}x total-latency speedup on the local proxy."
            ),
            "prefix_reuse": (
                f"The optimized capstone path reused {serving['optimized']['prefix_tokens_reused']} "
                "prefix tokens across logical prompts."
            ),
            "quantization": (
                f"The smallest measured scheme is {best_quant['scheme']} at {best_quant['memory_mb']} MB "
                f"with {best_quant['relative_error_pct']}% relative error."
            ),
            "deployment_runtime": (
                f"vLLM status is {vllm['result']['status']}: {vllm['result']['reason']}"
            ),
        },
        "capstone_result": {
            "high_level": serving["high_level"],
            "optimized": serving["optimized"],
            "blocked_runtime_areas": blocked,
        },
        "gpumode_deep_labs": [summarize_gpumode_lab(artifact) for artifact in gpumode_artifacts],
        "corpus_bridge": corpus_bridge(),
        "final_read": (
            "The runnable core now proves the teaching path on this machine: high-level HF inference, "
            "operation-level roofline measurements, attention/KV-cache behavior, quantization tradeoffs, "
            "JAX cost modeling, runtime readiness checks, GPUMODE-derived access-pattern, reduction/scan, Triton autotune, online-softmax, torch.compile, vLLM-style scheduler, quantized-matmul, and profiler-to-roofline measurement, "
            "shared-memory GEMM reuse, Tensor Core/CUTLASS readiness, ROCm/HIP portability, distributed collective modeling, "
            "and a measured capstone serving comparison. "
            "GPU-specific CUDA, Triton, HIP, and vLLM throughput remain environment-gated and are recorded "
            "as explicit skip artifacts rather than hidden assumptions."
        ),
    }
    out = {
        "session": "14-final-synthesis",
        "timestamp": now(),
        "inventory": collect_inventory("14-final-synthesis"),
        "artifacts_used": [
            "02-roofline",
            "05-cuda-tiny-attention",
            "08-quantized-inference",
            "09-vllm-serving",
            "10-kv-cache-memory-manager",
            "12-jax-scaling-practicum",
            "13-capstone-mini-serving-engine",
            *[str(Path(rel).parent) for rel in gpumode_sources if (ROOT / rel).exists()],
        ],
        "synthesis": synthesis,
        "boundary": (
            "This synthesis is generated from local artifacts. It explains the measured system state; "
            "it does not invent GPU benchmark numbers when this environment cannot run them."
        ),
    }
    path = HERE / "out_final_synthesis.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path.name)


def summarize_gpumode_lab(artifact: dict) -> dict:
    cpu = (
        artifact.get("cpu_proxy")
        or artifact.get("cpu_baseline")
        or artifact.get("online_softmax")
        or artifact.get("torch_compile")
        or artifact.get("scheduler")
        or artifact.get("quantized_matmul")
        or artifact.get("profiler_roofline")
        or artifact.get("shared_memory_gemm")
        or artifact.get("tensor_core_precision")
        or artifact.get("hip_portability")
        or artifact.get("collective_model")
        or artifact.get("config_model", {})
    )
    cuda = artifact.get("cuda") or artifact.get("triton") or {}
    finding = (
        cpu.get("finding")
        or artifact.get("config_model", {}).get("finding")
        or artifact.get("triton", {}).get("reason")
        or artifact.get("boundary", "")
    )
    return {
        "session": artifact["session"],
        "lab_id": artifact["source"]["gpumode_lab_id"],
        "lesson_anchor_count": len(artifact["source"]["gpumode_lessons"]),
        "cpu_finding": finding,
        "cuda_status": cuda.get("status"),
        "correctness": artifact["correctness"]["status"],
    }


if __name__ == "__main__":
    main()
