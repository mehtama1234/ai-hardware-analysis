"""Assemble generated session pages into gpu-kernels-serving-lab/site."""

from __future__ import annotations

import html
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"

SESSIONS = [
    (
        "00-orientation.html",
        "00-orientation/out/index.html",
        "00 - Orientation",
        "Detect the local CUDA/ROCm/JAX/Hugging Face/vLLM stack and render the serving pipeline map.",
        "live",
    ),
    (
        "01-hf-baseline.html",
        "01-hf-baseline/out/index.html",
        "01 - Hugging Face baseline",
        "Run model.generate, measure TTFT, tokens/sec, peak memory, and KV-cache estimates.",
        "live",
    ),
    (
        "02-roofline.html",
        "02-roofline/out/index.html",
        "02 - Roofline for AI ops",
        "Measure bandwidth, FLOP/s, arithmetic intensity, and attention/KV-cache pressure.",
        "live",
    ),
    (
        "03-cuda-vector-reduce.html",
        "03-cuda-vector-reduce/out/index.html",
        "03 - CUDA vector/reduce",
        "Write the first CUDA kernels and compare memory access patterns against PyTorch.",
        "live",
    ),
    (
        "04-cuda-tiled-matmul.html",
        "04-cuda-tiled-matmul/out/index.html",
        "04 - CUDA tiled matmul",
        "Use shared memory tiles to show why data reuse is the heart of fast GEMM.",
        "live",
    ),
    (
        "05-cuda-tiny-attention.html",
        "05-cuda-tiny-attention/out/index.html",
        "05 - CUDA tiny attention",
        "Measure materialized attention, SDPA, and causal KV-cache decode scaling.",
        "live",
    ),
    (
        "06-triton-matmul.html",
        "06-triton-matmul/out/index.html",
        "06 - Triton matmul",
        "Run or skip a readable blocked Triton matmul, then compare its role to CUDA and cuBLAS.",
        "live",
    ),
    (
        "07-triton-fused-attention.html",
        "07-triton-fused-attention/out/index.html",
        "07 - Triton fused attention",
        "Run or skip a single-query fused-attention Triton kernel with online softmax.",
        "live",
    ),
    (
        "08-quantized-inference.html",
        "08-quantized-inference/out/index.html",
        "08 - Quantized inference",
        "Measure memory savings and numerical drift before GPU-specific quantized kernels.",
        "live",
    ),
    (
        "09-vllm-serving.html",
        "09-vllm-serving/out/index.html",
        "09 - vLLM serving",
        "Record vLLM readiness and define the optimized serving benchmark boundary.",
        "live",
    ),
    (
        "10-kv-cache-memory-manager.html",
        "10-kv-cache-memory-manager/out/index.html",
        "10 - KV-cache memory manager",
        "Simulate block allocation, prefix reuse, and batch memory pressure.",
        "live",
    ),
    (
        "11-rocm-hip-port.html",
        "11-rocm-hip-port/out/index.html",
        "11 - ROCm/HIP port",
        "Compile or skip a minimal HIP vector kernel and record the CUDA-to-HIP translation.",
        "live",
    ),
    (
        "12-jax-scaling.html",
        "12-jax-scaling-practicum/out/index.html",
        "12 - JAX scaling practicum",
        "Run JAX jit timing, list devices, and compute explicit KV-cache sizing.",
        "live",
    ),
    (
        "13-capstone.html",
        "13-capstone-mini-serving-engine/out/index.html",
        "13 - Capstone diagnosis",
        "Aggregate all current artifacts into one end-to-end serving diagnosis and serving-path comparison.",
        "live",
    ),
    (
        "14-final-synthesis.html",
        "14-final-synthesis/out/index.html",
        "14 - Final synthesis",
        "Tie the measured lab back to compute, memory, communication, KV cache, batching, prefix reuse, quantization, and runtime deployment.",
        "live",
    ),
    (
        "15-gpumode-coalescing.html",
        "15-gpumode-coalescing/out/index.html",
        "15 - GPUMODE coalescing",
        "Use GPUMODE transcript intelligence to drive a CUDA and PyTorch memory-access microscope.",
        "live",
    ),
    (
        "16-gpumode-warp-reductions.html",
        "16-gpumode-warp-reductions/out/index.html",
        "16 - GPUMODE warp reductions",
        "Turn warp-execution lessons into reduction and scan measurements with CUDA reduction source.",
        "live",
    ),
    (
        "17-gpumode-triton-autotune.html",
        "17-gpumode-triton-autotune/out/index.html",
        "17 - GPUMODE Triton autotune",
        "Rank Triton matmul tile candidates, record a CPU baseline, and sweep kernels when CUDA is visible.",
        "live",
    ),
    (
        "18-gpumode-online-softmax.html",
        "18-gpumode-online-softmax/out/index.html",
        "18 - GPUMODE online softmax",
        "Compare materialized attention with an online softmax recurrence and CUDA-gated fused-kernel path.",
        "live",
    ),
    (
        "19-gpumode-torch-compile.html",
        "19-gpumode-torch-compile/out/index.html",
        "19 - GPUMODE torch.compile",
        "Measure eager versus compiled PyTorch paths and inspect graph-break behavior.",
        "live",
    ),
    (
        "20-gpumode-vllm-scheduler.html",
        "20-gpumode-vllm-scheduler/out/index.html",
        "20 - GPUMODE vLLM scheduler",
        "Compare static batches with continuous batching and paged prefix-cache accounting.",
        "live",
    ),
    (
        "21-gpumode-quantized-kernels.html",
        "21-gpumode-quantized-kernels/out/index.html",
        "21 - GPUMODE quantized kernels",
        "Compare fp16, int8, int4, and MXFP4-like matmul paths with error and memory accounting.",
        "live",
    ),
    (
        "22-gpumode-nsight-roofline.html",
        "22-gpumode-nsight-roofline/out/index.html",
        "22 - GPUMODE Nsight to roofline",
        "Map profiler counters to roofline bottleneck classes and next optimization actions.",
        "live",
    ),
    (
        "23-gpumode-shared-memory-gemm.html",
        "23-gpumode-shared-memory-gemm/out/index.html",
        "23 - GPUMODE shared-memory GEMM",
        "Measure naive versus tiled GEMM and model shared-memory reuse before CUTLASS/Tensor Core kernels.",
        "live",
    ),
    (
        "24-gpumode-tensor-core-cutlass.html",
        "24-gpumode-tensor-core-cutlass/out/index.html",
        "24 - GPUMODE Tensor Core/CUTLASS",
        "Measure low-precision matmul drift, model MMA tile eligibility, and record CUDA/CUTLASS readiness.",
        "live",
    ),
    (
        "25-gpumode-rocm-hip-portability.html",
        "25-gpumode-rocm-hip-portability/out/index.html",
        "25 - GPUMODE ROCm/HIP portability",
        "Translate selected CUDA kernels to HIP, validate semantics, and identify real portability boundaries.",
        "live",
    ),
    (
        "26-gpumode-distributed-communication.html",
        "26-gpumode-distributed-communication/out/index.html",
        "26 - GPUMODE distributed communication",
        "Model all-reduce and NVSHMEM-style regimes, validate local semantics, and record NCCL/NVSHMEM readiness.",
        "live",
    ),
]


def esc(value: object) -> str:
    return html.escape(str(value))


def card(filename: str, title: str, summary: str, status: str) -> str:
    href = filename if status == "live" else "#"
    cls = "live" if status == "live" else "planned"
    return (
        f'<a class="card {cls}" href="{href}">'
        f'<span class="status">{esc(status)}</span>'
        f"<h2>{esc(title)}</h2>"
        f"<p>{esc(summary)}</p>"
        "</a>"
    )


def nav() -> str:
    links = []
    for filename, source, title, _summary, status in SESSIONS:
        if status == "live":
            links.append(f'<a href="{filename}">{esc(title)}</a>')
    return '<nav><a href="index.html" class="brand">GPU Serving Lab</a><span>' + "".join(links) + "</span></nav>"


def wrap_session(doc: str) -> str:
    return doc.replace('<div class="wrap">', '<div class="wrap">\n' + nav(), 1)


def build() -> None:
    SITE.mkdir(exist_ok=True)
    for filename, source, _title, _summary, status in SESSIONS:
        if status != "live" or source is None:
            continue
        doc = (ROOT / source).read_text(encoding="utf-8")
        (SITE / filename).write_text(wrap_session(doc), encoding="utf-8")

    cards = "\n".join(card(filename, title, summary, status) for filename, _source, title, summary, status in SESSIONS)
    land = f"""<meta charset="utf-8">
<title>GPU Kernels And LLM Serving Lab</title>
<style>
:root{{--bg:#0E1420;--bg2:#141D2C;--ink:#EAEEF4;--soft:#B4BFD0;--dim:#8493A8;--faint:#5A6577;--line:rgba(150,170,205,.14);--accent:#4FA8B8;--serif:"Iowan Old Style",Palatino,Georgia,serif;--sans:-apple-system,system-ui,"Segoe UI",Roboto,Arial,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.7}}
.wrap{{max-width:900px;margin:0 auto;padding:64px 24px 80px}}.kick{{font-family:var(--mono);font-size:11.5px;letter-spacing:.22em;text-transform:uppercase;color:var(--accent)}}
h1{{font-family:var(--serif);font-size:clamp(34px,6vw,54px);line-height:1.05;margin:14px 0 0;color:#fff}}.dek{{font-size:19px;color:var(--soft);max-width:68ch;margin-top:18px}}
.grid{{display:grid;gap:12px;margin-top:34px}}.card{{display:block;text-decoration:none;background:var(--bg2);border:1px solid var(--line);border-radius:12px;padding:18px 20px;color:inherit}}
.card.live:hover{{border-color:var(--accent)}}.card.planned{{opacity:.58;cursor:default}}.card h2{{font-family:var(--serif);font-size:22px;color:#fff;margin:4px 0 8px}}.card p{{margin:0;color:var(--soft);font-size:14.5px}}
.status{{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}}.card.planned .status{{color:var(--faint)}}
.src{{font-family:var(--mono);font-size:12px;color:var(--faint);margin-top:28px;padding-top:16px;border-top:1px solid var(--line)}}a{{color:var(--accent)}}
</style>
<div class="wrap">
  <div class="kick">Hands-on GPU systems track</div>
  <h1>GPU kernels and LLM serving, end to end.</h1>
  <p class="dek">A runnable path from Hugging Face model APIs down to memory movement,
  kernels, quantization, KV-cache management, vLLM serving, ROCm/HIP portability, and JAX
  scaling analysis. Every completed page is generated from measurement artifacts.</p>
  <div class="grid">{cards}</div>
  <div class="src">Goal spec: <a href="MEATY-GOAL.md">MEATY-GOAL.md</a>. Source spine:
  JAX Scaling Book, Hugging Face tutorials, vLLM docs, Triton tutorials, CUDA guide, and
  ROCm/HIP docs.</div>
</div>
"""
    (SITE / "index.html").write_text(land, encoding="utf-8")
    shutil.copyfile(ROOT / "MEATY-GOAL.md", SITE / "MEATY-GOAL.md")
    print("wrote", SITE)


if __name__ == "__main__":
    build()
