#!/usr/bin/env python3
"""Build a queryable GPU systems workbench from curriculum, lab, and corpus artifacts."""

from __future__ import annotations

import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
CURRICULUM = ROOT / "analysis" / "gpumode-curriculum.json"
CURRICULUM_GRAPH = ROOT / "analysis" / "curriculum-graph.json"
LESSON_INTELLIGENCE = ROOT / "analysis" / "lesson-intelligence.json"
LAB_ROOT = REPO / "gpu-kernels-serving-lab"
PAPER_ROOT = REPO / "analysis" / "per-paper"
ANALYSIS = ROOT / "analysis"
SITE = ROOT / "site"
OUT_JSON = ANALYSIS / "gpu-systems-workbench.json"
OUT_HTML = SITE / "workbench.html"
TUTORIAL_SOURCES_JSON = ANALYSIS / "tutorial-sources.json"
TUTORIAL_EXERCISE_PATHS_JSON = ANALYSIS / "tutorial-exercise-paths.json"
LESSON_CORPUS_BRIDGES_JSON = ANALYSIS / "lesson-corpus-bridges.json"
LATEST_MEASUREMENTS_JSON = ANALYSIS / "latest-measurements-index.json"

STOPWORDS = {
    "about",
    "after",
    "also",
    "and",
    "are",
    "before",
    "between",
    "from",
    "for",
    "how",
    "into",
    "model",
    "one",
    "that",
    "the",
    "their",
    "then",
    "this",
    "through",
    "using",
    "when",
    "where",
    "while",
    "with",
}


PROFILES = [
    {
        "id": "memory-bandwidth",
        "label": "Memory bandwidth / layout bottleneck",
        "query_terms": [
            "memory",
            "bandwidth",
            "coalescing",
            "global memory",
            "layout",
            "roofline",
            "kv cache",
            "cache",
            "hbm",
        ],
        "lesson_topics": ["cuda", "profiling", "hardware", "attention"],
        "lesson_concepts": ["memory coalescing", "kv cache", "profiling workflow", "shared memory tiling"],
        "lab_ids": ["gpumode-lab-01-coalescing", "gpumode-lab-08-nsight-to-roofline", "gpumode-lab-09-shared-memory-gemm"],
        "artifact_terms": ["roofline", "coalescing", "kv_cache", "attention", "shared_memory_gemm", "tiled_bytes"],
        "paper_terms": ["memory", "bandwidth", "cache", "dram", "hbm", "prefetch", "roofline", "gpu"],
    },
    {
        "id": "profiling-roofline",
        "label": "Profiler counters / roofline triage",
        "query_terms": [
            "profile",
            "profiler",
            "profiling",
            "nsight",
            "ncu",
            "nsys",
            "counter",
            "roofline",
            "dram",
            "sm utilization",
            "stall",
            "occupancy",
            "launch overhead",
            "bottleneck",
        ],
        "lesson_topics": ["profiling", "hardware", "cuda"],
        "lesson_concepts": ["profiling workflow", "memory coalescing", "occupancy", "warp execution"],
        "lab_ids": [
            "gpumode-lab-08-nsight-to-roofline",
            "gpumode-lab-01-coalescing",
            "gpumode-lab-02-warp-reductions",
            "gpumode-lab-09-shared-memory-gemm",
        ],
        "artifact_terms": ["profiler_roofline", "nsight", "counter", "roofline", "dram", "sm__", "stall", "occupancy", "arithmetic_intensity"],
        "paper_terms": ["profiling", "profiler", "roofline", "counter", "performance", "gpu", "memory", "compute"],
    },
    {
        "id": "warp-synchronization",
        "label": "Warp execution / synchronization bottleneck",
        "query_terms": [
            "warp",
            "reduction",
            "scan",
            "shuffle",
            "shared memory",
            "synchronization",
            "occupancy",
        ],
        "lesson_topics": ["cuda", "hardware", "profiling"],
        "lesson_concepts": ["warp execution", "shared memory tiling", "occupancy", "profiling workflow"],
        "lab_ids": ["gpumode-lab-02-warp-reductions"],
        "artifact_terms": ["reduction", "warp", "scan", "cuda_vector_reduce"],
        "paper_terms": ["warp", "synchronization", "gpu", "parallel", "occupancy", "memory-system"],
    },
    {
        "id": "triton-autotune",
        "label": "Triton custom-kernel / autotuning path",
        "query_terms": ["triton", "autotune", "block", "program id", "matmul", "tl.load", "tl.store"],
        "lesson_topics": ["triton", "profiling"],
        "lesson_concepts": ["autotuning", "shared memory tiling"],
        "lab_ids": ["gpumode-lab-03-triton-autotune", "gpumode-lab-09-shared-memory-gemm"],
        "artifact_terms": ["triton", "matmul", "fused_attention", "shared_memory_gemm", "tile"],
        "paper_terms": ["compiler", "kernel", "matmul", "fusion", "gpu", "autotuning", "pytorch"],
    },
    {
        "id": "tensor-core-cutlass",
        "label": "Tensor Core / CUTLASS matmul path",
        "query_terms": [
            "tensor core",
            "tensor cores",
            "cutlass",
            "cute",
            "wmma",
            "wgmma",
            "mma",
            "tf32",
            "bf16",
            "fp16",
            "matmul",
            "gemm",
            "tile eligibility",
            "epilogue",
        ],
        "lesson_topics": ["cuda", "hardware", "cutlass", "quantization"],
        "lesson_concepts": ["tensor cores", "shared memory tiling", "quantized numerics", "profiling workflow"],
        "lab_ids": ["gpumode-lab-10-tensor-core-cutlass", "gpumode-lab-09-shared-memory-gemm", "gpumode-lab-07-quantized-kernels"],
        "artifact_terms": ["tensor_core", "cutlass", "wmma", "wgmma", "mma", "bf16", "fp16", "tile_model"],
        "paper_terms": ["tensor core", "cutlass", "matmul", "gemm", "low-precision", "fp16", "bf16", "tf32", "accelerator", "gpu"],
    },
    {
        "id": "rocm-hip-portability",
        "label": "ROCm/HIP portability path",
        "query_terms": [
            "rocm",
            "hip",
            "hipcc",
            "amd",
            "cuda to hip",
            "portability",
            "port",
            "lds",
            "wavefront",
            "rocwmma",
            "composable kernel",
        ],
        "lesson_topics": ["cuda", "hardware", "distributed", "cutlass"],
        "lesson_concepts": ["shared memory tiling", "warp execution", "tensor cores", "collectives", "profiling workflow"],
        "lab_ids": ["gpumode-lab-11-rocm-hip-portability", "gpumode-lab-09-shared-memory-gemm", "gpumode-lab-10-tensor-core-cutlass"],
        "artifact_terms": ["hip_portability", "hipcc", "rocm", "translated.hip", "cuda-to-hip", "wmma", "manual-port"],
        "paper_terms": ["amd", "rocm", "hip", "portability", "gpu", "wavefront", "memory", "compiler", "distributed"],
    },
    {
        "id": "pytorch-compiler-fusion",
        "label": "PyTorch compiler / graph-break bottleneck",
        "query_terms": [
            "torch",
            "compile",
            "torch.compile",
            "inductor",
            "dynamo",
            "aot",
            "fx",
            "graph break",
            "fusion",
            "kernel fusion",
            "compiler",
        ],
        "lesson_topics": ["pytorch-compiler", "triton", "profiling"],
        "lesson_concepts": ["compiler lowering", "kernel fusion", "autotuning", "profiling workflow"],
        "lab_ids": ["gpumode-lab-05-torch-compile", "gpumode-lab-03-triton-autotune"],
        "artifact_terms": ["torch_compile", "torch.compile", "graph_break", "inductor", "dynamo", "compile"],
        "paper_terms": ["compiler", "fusion", "pytorch", "graph", "kernel", "mlir", "inductor", "aot"],
    },
    {
        "id": "attention-serving",
        "label": "Attention, KV cache, and serving bottleneck",
        "query_terms": [
            "attention",
            "kv cache",
            "pagedattention",
            "prefill",
            "decode",
            "vllm",
            "serving",
            "batching",
            "prefix",
        ],
        "lesson_topics": ["attention", "serving", "triton", "cuda"],
        "lesson_concepts": ["online softmax", "kv cache", "kernel fusion", "profiling workflow"],
        "lab_ids": ["gpumode-lab-04-online-softmax", "gpumode-lab-06-vllm-scheduler"],
        "artifact_terms": ["attention", "kv_cache", "vllm", "capstone", "serving"],
        "paper_terms": ["attention", "serving", "inference", "llm", "kv", "cache", "batching", "gpu"],
    },
    {
        "id": "serving-scheduler",
        "label": "vLLM scheduler / TTFT and batching bottleneck",
        "query_terms": [
            "vllm",
            "scheduler",
            "scheduling",
            "ttft",
            "tpot",
            "continuous batching",
            "batching",
            "pagedattention",
            "paged attention",
            "prefix cache",
            "prefix caching",
            "chunked prefill",
            "prefill",
            "decode",
            "kv cache",
            "sla",
        ],
        "lesson_topics": ["serving", "attention", "profiling"],
        "lesson_concepts": ["kv cache", "profiling workflow"],
        "lab_ids": ["gpumode-lab-06-vllm-scheduler", "gpumode-lab-04-online-softmax"],
        "artifact_terms": ["vllm_scheduler", "scheduler", "ttft", "tpot", "continuous", "prefix_cache", "serving"],
        "paper_terms": ["scheduler", "serving", "batching", "ttft", "latency", "sla", "kv", "cache", "inference"],
    },
    {
        "id": "quantized-numerics",
        "label": "Quantization / low-precision numerics path",
        "query_terms": ["quantization", "int8", "int4", "fp8", "mxfp", "nvfp4", "bitsandbytes"],
        "lesson_topics": ["quantization", "hardware", "serving"],
        "lesson_concepts": ["quantized numerics", "tensor cores", "profiling workflow"],
        "lab_ids": ["gpumode-lab-07-quantized-kernels"],
        "artifact_terms": ["quantized", "quantization", "fp16", "int8", "int4"],
        "paper_terms": ["quantization", "int8", "int4", "fp8", "low-precision", "inference", "accelerator"],
    },
    {
        "id": "distributed-communication",
        "label": "Distributed communication / collective bottleneck",
        "query_terms": ["distributed", "collective", "all-reduce", "nccl", "nvshmem", "communication", "topology"],
        "lesson_topics": ["distributed", "profiling", "hardware"],
        "lesson_concepts": ["collectives", "profiling workflow", "kv cache"],
        "lab_ids": [
            "gpumode-lab-12-distributed-communication",
            "gpumode-lab-08-nsight-to-roofline",
            "gpumode-lab-11-rocm-hip-portability",
        ],
        "artifact_terms": ["collective_model", "allreduce", "all-reduce", "nvshmem", "nccl", "communication", "devices", "hip_portability", "collectives"],
        "paper_terms": ["distributed", "communication", "collective", "topology", "interconnect", "gpu", "hpc"],
    },
]

TUTORIAL_SOURCES = [
    {
        "id": "cuda-programming-guide",
        "provider": "NVIDIA",
        "title": "CUDA C++ Programming Guide",
        "url": "https://docs.nvidia.com/cuda/cuda-programming-guide/index.html",
        "focus_terms": ["cuda", "thread", "block", "memory", "shared memory", "warp", "programming model"],
        "profile_ids": ["memory-bandwidth", "warp-synchronization", "tensor-core-cutlass", "profiling-roofline"],
        "why": "Use this as the official CUDA programming-model reference behind the memory, warp, and matmul kernel labs.",
    },
    {
        "id": "cuda-best-practices",
        "provider": "NVIDIA",
        "title": "CUDA C++ Best Practices Guide",
        "url": "https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html",
        "focus_terms": ["cuda", "performance", "optimization", "memory coalescing", "occupancy", "profiling"],
        "profile_ids": ["memory-bandwidth", "profiling-roofline", "warp-synchronization", "tensor-core-cutlass"],
        "why": "Use this to turn profiler symptoms into concrete CUDA optimization checks.",
    },
    {
        "id": "triton-official-tutorials",
        "provider": "Triton",
        "title": "Triton Tutorials",
        "url": "https://triton-lang.org/main/getting-started/tutorials/",
        "focus_terms": ["triton", "vector addition", "fused softmax", "matrix multiplication", "layer normalization", "autotune"],
        "profile_ids": ["triton-autotune", "attention-serving", "pytorch-compiler-fusion"],
        "why": "Use this as the official progression from simple Triton kernels to fused softmax and matmul tuning.",
    },
    {
        "id": "triton-fused-softmax",
        "provider": "Triton",
        "title": "Fused Softmax Tutorial",
        "url": "https://triton-lang.org/main/getting-started/tutorials/02-fused-softmax.html",
        "focus_terms": ["triton", "softmax", "fusion", "bandwidth-bound", "reduction", "sram"],
        "profile_ids": ["triton-autotune", "attention-serving", "memory-bandwidth"],
        "why": "Use this to connect Triton fusion and reductions to the online-softmax and attention labs.",
    },
    {
        "id": "rocm-hip-docs",
        "provider": "AMD ROCm",
        "title": "HIP Documentation",
        "url": "https://rocm.docs.amd.com/projects/HIP/en/latest/",
        "focus_terms": ["hip", "rocm", "amd", "cuda portability", "kernel programming", "runtime api"],
        "profile_ids": ["rocm-hip-portability", "distributed-communication"],
        "why": "Use this as the official HIP reference for porting CUDA-shaped kernels to AMD GPUs.",
    },
    {
        "id": "rocm-hip-programming-model",
        "provider": "AMD ROCm",
        "title": "Introduction to the HIP Programming Model",
        "url": "https://rocm.docs.amd.com/projects/HIP/en/latest/understand/programming_model.html",
        "focus_terms": ["hip", "programming model", "simd", "kernel", "memory", "amd gpu"],
        "profile_ids": ["rocm-hip-portability", "warp-synchronization", "memory-bandwidth"],
        "why": "Use this to compare CUDA block/warp assumptions with HIP's AMD GPU execution model.",
    },
    {
        "id": "jax-scaling-roofline",
        "provider": "JAX Scaling Book",
        "title": "All About Rooflines",
        "url": "https://jax-ml.github.io/scaling-book/roofline/",
        "focus_terms": ["roofline", "flops", "memory bandwidth", "communication", "compute", "latency"],
        "profile_ids": ["memory-bandwidth", "profiling-roofline", "distributed-communication"],
        "why": "Use this as the math lens for deciding whether compute, memory, or communication dominates an LLM workload.",
    },
    {
        "id": "jax-scaling-training",
        "provider": "JAX Scaling Book",
        "title": "How to Parallelize a Transformer for Training",
        "url": "https://jax-ml.github.io/scaling-book/training/",
        "focus_terms": ["parallelism", "training", "data parallel", "tensor parallel", "pipeline", "communication"],
        "profile_ids": ["distributed-communication", "pytorch-compiler-fusion"],
        "why": "Use this to connect local collectives and compiler behavior to large-model sharding choices.",
    },
    {
        "id": "jax-scaling-inference",
        "provider": "JAX Scaling Book",
        "title": "All About Transformer Inference",
        "url": "https://jax-ml.github.io/scaling-book/inference/",
        "focus_terms": ["inference", "kv cache", "prefill", "decode", "batching", "latency", "throughput"],
        "profile_ids": ["attention-serving", "serving-scheduler", "memory-bandwidth"],
        "why": "Use this to ground prefill/decode, KV-cache, and batching measurements in an explicit inference cost model.",
    },
    {
        "id": "jax-scaling-applied-inference",
        "provider": "JAX Scaling Book",
        "title": "Serving LLaMA 3-70B on TPUs",
        "url": "https://jax-ml.github.io/scaling-book/applied-inference/",
        "focus_terms": ["serving", "llama", "kv cache", "batch size", "roofline", "latency", "throughput"],
        "profile_ids": ["attention-serving", "serving-scheduler", "distributed-communication"],
        "why": "Use this as a worked serving-capacity example to compare against the vLLM-style scheduler lab.",
    },
    {
        "id": "jax-scaling-profiling",
        "provider": "JAX Scaling Book",
        "title": "How to Profile TPU Programs",
        "url": "https://jax-ml.github.io/scaling-book/profiling/",
        "focus_terms": ["profiling", "xla", "profiler", "tensorboard", "compiler", "trace"],
        "profile_ids": ["profiling-roofline", "pytorch-compiler-fusion"],
        "why": "Use this to compare theoretical roofline reasoning with profiler-driven compiler/runtime debugging.",
    },
    {
        "id": "jax-scaling-programming",
        "provider": "JAX Scaling Book",
        "title": "Programming TPUs in JAX",
        "url": "https://jax-ml.github.io/scaling-book/jax-stuff/",
        "focus_terms": ["jax", "jit", "sharding", "xla", "parallelism", "profiling"],
        "profile_ids": ["pytorch-compiler-fusion", "distributed-communication"],
        "why": "Use this to compare JAX/XLA programming patterns with PyTorch compiler and distributed-runtime labs.",
    },
    {
        "id": "jax-scaling-gpus",
        "provider": "JAX Scaling Book",
        "title": "How to Think About GPUs",
        "url": "https://jax-ml.github.io/scaling-book/gpus/",
        "focus_terms": ["gpu", "hbm", "sm", "tensor cores", "network", "nvidia", "memory"],
        "profile_ids": ["memory-bandwidth", "tensor-core-cutlass", "distributed-communication", "profiling-roofline"],
        "why": "Use this as the hardware mental model for SMs, HBM, Tensor Cores, and GPU interconnects.",
    },
    {
        "id": "hf-llm-optimized-inference",
        "provider": "Hugging Face",
        "title": "LLM Course: Optimized Inference Deployment",
        "url": "https://huggingface.co/learn/llm-course/chapter2/8",
        "focus_terms": ["tgi", "vllm", "llama.cpp", "deployment", "serving", "inference"],
        "profile_ids": ["serving-scheduler", "attention-serving"],
        "why": "Use this to place the local vLLM-style scheduler lab in the production-serving framework landscape.",
    },
    {
        "id": "hf-transformers-pipelines",
        "provider": "Hugging Face",
        "title": "Transformers Pipelines",
        "url": "https://huggingface.co/docs/transformers/en/main_classes/pipelines",
        "focus_terms": ["pipeline", "inference", "transformers", "preprocessing", "postprocessing"],
        "profile_ids": ["attention-serving", "serving-scheduler"],
        "why": "Use this as the high-level API baseline before dropping down to kernels, batching, and memory behavior.",
    },
    {
        "id": "hf-transformers-causal-lm",
        "provider": "Hugging Face",
        "title": "Transformers: Causal Language Modeling",
        "url": "https://huggingface.co/docs/transformers/en/tasks/language_modeling",
        "focus_terms": ["causal language modeling", "text generation", "inference", "tokenization", "transformers"],
        "profile_ids": ["attention-serving", "serving-scheduler"],
        "why": "Use this to connect model-level text generation to prefill/decode and KV-cache mechanics.",
    },
    {
        "id": "hf-transformers-quantization",
        "provider": "Hugging Face",
        "title": "Transformers Quantization",
        "url": "https://huggingface.co/docs/transformers/en/quantization/overview",
        "focus_terms": ["quantization", "bitsandbytes", "int8", "int4", "fp8", "memory"],
        "profile_ids": ["quantized-numerics", "tensor-core-cutlass", "memory-bandwidth"],
        "why": "Use this to compare framework quantization choices with the local numerical-drift and kernel-readiness labs.",
    },
    {
        "id": "hf-tgi-overview",
        "provider": "Hugging Face",
        "title": "Text Generation Inference Documentation",
        "url": "https://huggingface.co/docs/text-generation-inference/index",
        "focus_terms": ["text generation inference", "tgi", "serving", "continuous batching", "streaming"],
        "profile_ids": ["serving-scheduler", "attention-serving", "distributed-communication"],
        "why": "Use this as the production serving counterpart to the local scheduler, KV-cache, and collective-latency labs.",
    },
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def text_blob(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{k} {text_blob(v)}" for k, v in value.items())
    if isinstance(value, list):
        return " ".join(text_blob(v) for v in value)
    return str(value)


def score_text(text: str, terms: list[str]) -> int:
    lower = text.lower()
    return sum(1 for term in terms if term.lower() in lower)


def tokens(value: Any) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9.+_-]*", text_blob(value).lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def lesson_score(lesson: dict[str, Any], profile: dict[str, Any]) -> int:
    score = 0
    score += 4 * len(set(lesson.get("topics", [])).intersection(profile["lesson_topics"]))
    score += 5 * len(set(lesson.get("concepts", [])).intersection(profile["lesson_concepts"]))
    score += 2 * score_text(text_blob(lesson.get("exercise_candidates", [])), profile["query_terms"])
    score += score_text(lesson.get("title", ""), profile["query_terms"])
    return score


def lab_score(lab: dict[str, Any], profile: dict[str, Any]) -> int:
    score = 8 if lab["id"] in profile["lab_ids"] else 0
    score += 3 * len(set(lab.get("topics", [])).intersection(profile["lesson_topics"]))
    score += score_text(text_blob(lab), profile["query_terms"])
    return score


def paper_score(paper: dict[str, Any], profile: dict[str, Any]) -> int:
    fields = [
        paper.get("title", ""),
        paper.get("venue", ""),
        paper.get("primary_theme", ""),
        paper.get("problem", ""),
        paper.get("method", ""),
        paper.get("key_novelty", ""),
        paper.get("hardware_target", []),
        paper.get("technique_category", []),
        paper.get("workloads", []),
        paper.get("tags", []),
    ]
    score = score_text(text_blob(fields), profile["paper_terms"])
    if any("gpu" in str(target).lower() for target in paper.get("hardware_target", [])):
        score += 2
    if str(paper.get("confidence", "")).lower() == "high":
        score += 1
    return score


def tutorial_score(source: dict[str, Any], profile: dict[str, Any]) -> int:
    score = 10 if profile["id"] in source.get("profile_ids", []) else 0
    score += score_text(text_blob(source.get("focus_terms", [])), profile["query_terms"])
    score += score_text(text_blob([source.get("title", ""), source.get("why", "")]), profile["query_terms"])
    return score


def collect_tutorial_sources(profile: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for source in TUTORIAL_SOURCES:
        score = tutorial_score(source, profile)
        if score <= 0:
            continue
        rows.append(
            {
                "id": source["id"],
                "provider": source["provider"],
                "title": source["title"],
                "url": source["url"],
                "focus_terms": source["focus_terms"],
                "why": source["why"],
                "score": score,
            }
        )
    return sorted(rows, key=lambda row: (-row["score"], row["provider"], row["title"]))[:6]


def build_exercise_path(
    profile: dict[str, Any],
    lessons: list[dict[str, Any]],
    labs: list[dict[str, Any]],
    measurements: list[dict[str, Any]],
    tutorial_sources: list[dict[str, Any]],
    papers: list[dict[str, Any]],
) -> dict[str, Any]:
    implemented_lab = next((lab for lab in labs if lab.get("status") == "implemented"), labs[0] if labs else {})
    primary_lesson = lessons[0] if lessons else {}
    primary_measurement = measurements[0] if measurements else {}
    primary_source = tutorial_sources[0] if tutorial_sources else {}
    primary_paper = papers[0] if papers else {}
    command = ""
    if implemented_lab.get("implemented_as"):
        command = f"cd ../{implemented_lab['implemented_as']} && python3 run.py && python3 build_page.py"
    return {
        "id": f"{profile['id']}-end-to-end-path",
        "title": f"{profile['label']} end-to-end tutorial path",
        "profile_id": profile["id"],
        "objective": diagnosis_for(profile["id"]),
        "source_reading": {
            "provider": primary_source.get("provider", ""),
            "title": primary_source.get("title", ""),
            "url": primary_source.get("url", ""),
            "why": primary_source.get("why", ""),
        },
        "gpumode_anchor": {
            "index": primary_lesson.get("index"),
            "title": primary_lesson.get("title", ""),
            "url": primary_lesson.get("url", ""),
            "concepts": primary_lesson.get("concepts", [])[:5],
        },
        "lab": {
            "id": implemented_lab.get("id", ""),
            "title": implemented_lab.get("title", ""),
            "path": implemented_lab.get("implemented_as", ""),
            "command": command,
        },
        "measurement": {
            "path": primary_measurement.get("path", ""),
            "summary": primary_measurement.get("summary", ""),
        },
        "paper_check": {
            "title": primary_paper.get("title", ""),
            "path": primary_paper.get("path", ""),
        },
        "steps": [
            f"Read {primary_source.get('provider', 'the external source')} - {primary_source.get('title', 'source')} and write down the claimed bottleneck model.",
            f"Open GPUMODE lesson #{primary_lesson.get('index', '')}: {primary_lesson.get('title', 'recommended lesson')} and extract the kernel/runtime concept that should be measurable.",
            f"Run {implemented_lab.get('implemented_as', 'the recommended lab')} and preserve the generated JSON artifact.",
            f"Compare {primary_measurement.get('path', 'the latest measurement artifact')} against the source model and the GPUMODE lesson concept.",
            f"Use {primary_paper.get('title', 'the top related corpus paper')} as the research cross-check for whether this bottleneck appears in current AI systems work.",
        ],
        "success_checks": [
            "Correctness status is passed or the artifact records an explicit environment-gated skip.",
            "The generated tutorial page names the same bottleneck class as the workbench profile.",
            "The measurement summary explains what changed or why real GPU execution was unavailable.",
            "At least one GPUMODE lesson, external tutorial source, and corpus paper can be traversed from the profile page.",
        ],
    }


def artifact_label(path: Path) -> str:
    return str(path.relative_to(LAB_ROOT))


def collect_measurements(profile: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(LAB_ROOT.glob("**/out_*.json")):
        data = read_json(path, {})
        blob = text_blob(data)
        score = score_text(f"{artifact_label(path)} {blob}", profile["artifact_terms"])
        source = data.get("source", {})
        source_lab_id = source.get("gpumode_lab_id") if isinstance(source, dict) else None
        if source_lab_id in profile.get("lab_ids", []):
            score += 8
        if score <= 0:
            continue
        rows.append(
            {
                "path": artifact_label(path),
                "session": data.get("session", path.parent.name),
                "status": artifact_status(data),
                "cuda_status": data.get("cuda", {}).get("status") or data.get("triton", {}).get("status"),
                "summary": summarize_artifact(data),
                "score": score,
            }
        )
    return sorted(rows, key=lambda row: (-row["score"], row["path"]))[:8]


def artifact_status(data: dict[str, Any]) -> str:
    return (
        data.get("status")
        or data.get("cpu_proxy", {}).get("status")
        or data.get("cpu_baseline", {}).get("status")
        or data.get("online_softmax", {}).get("status")
        or data.get("torch_compile", {}).get("status")
        or data.get("scheduler", {}).get("status")
        or data.get("quantized_matmul", {}).get("status")
        or data.get("profiler_roofline", {}).get("status")
        or data.get("shared_memory_gemm", {}).get("status")
        or data.get("tensor_core_precision", {}).get("status")
        or data.get("hip_portability", {}).get("status")
        or data.get("collective_model", {}).get("status")
        or data.get("result", {}).get("status")
        or data.get("config_model", {}).get("status")
        or "available"
    )


def runtime_readiness(data: dict[str, Any]) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for name in ("cuda", "triton", "hip", "vllm", "jax"):
        value = data.get(name)
        if isinstance(value, dict):
            rows[name] = {
                "status": value.get("status") or value.get("available"),
                "reason": value.get("reason") or value.get("boundary") or value.get("finding"),
            }
    result = data.get("result", {})
    if isinstance(result, dict) and result.get("status") == "skipped":
        rows.setdefault("primary", {})["status"] = "skipped"
        rows.setdefault("primary", {})["reason"] = result.get("reason") or result.get("boundary")
    runtime = data.get("runtime_readiness", {})
    if isinstance(runtime, dict):
        rows["runtime_readiness"] = runtime
    return rows


def collect_latest_measurement_index() -> dict[str, Any]:
    rows = []
    for path in sorted(LAB_ROOT.glob("**/out_*.json")):
        data = read_json(path, {})
        session = data.get("session", path.parent.name)
        rel = artifact_label(path)
        page = path.parent / "out" / "index.html"
        rows.append(
            {
                "path": rel,
                "session": session,
                "timestamp": data.get("timestamp", ""),
                "status": artifact_status(data),
                "correctness": data.get("correctness", {}).get("status"),
                "summary": summarize_artifact(data),
                "runtime_readiness": runtime_readiness(data),
                "source_gpumode_lab_id": data.get("source", {}).get("gpumode_lab_id") if isinstance(data.get("source"), dict) else None,
                "source_lesson_count": len(data.get("source", {}).get("gpumode_lessons", [])) if isinstance(data.get("source"), dict) else 0,
                "page": str(page.relative_to(LAB_ROOT)) if page.exists() else "",
            }
        )
    return {
        "generated_at": now(),
        "artifact_count": len(rows),
        "passed_correctness": sum(1 for row in rows if row.get("correctness") == "passed"),
        "skipped_runtime_count": sum(
            1
            for row in rows
            if any(
                isinstance(value, dict) and value.get("status") == "skipped"
                for value in row.get("runtime_readiness", {}).values()
            )
            or row.get("status") == "skipped"
        ),
        "rows": rows,
    }


def summarize_artifact(data: dict[str, Any]) -> str:
    if "cpu_proxy" in data and data["cpu_proxy"].get("finding"):
        return data["cpu_proxy"]["finding"]
    if "online_softmax" in data and data["online_softmax"].get("finding"):
        return data["online_softmax"]["finding"]
    if "torch_compile" in data and data["torch_compile"].get("finding"):
        return data["torch_compile"]["finding"]
    if "scheduler" in data and data["scheduler"].get("finding"):
        return data["scheduler"]["finding"]
    if "quantized_matmul" in data and data["quantized_matmul"].get("finding"):
        return data["quantized_matmul"]["finding"]
    imported_profiler = data.get("profiler_roofline", {}).get("imported_reports", {})
    if imported_profiler.get("status") == "ran":
        classes = imported_profiler.get("classifications", [])
        counts = Counter(row.get("bottleneck", "unknown") for row in classes)
        return f"{imported_profiler.get('finding')} Imported bottleneck counts: {dict(counts)}."
    if "profiler_roofline" in data and data["profiler_roofline"].get("finding"):
        return data["profiler_roofline"]["finding"]
    if "shared_memory_gemm" in data and data["shared_memory_gemm"].get("finding"):
        return data["shared_memory_gemm"]["finding"]
    if "tensor_core_precision" in data and data["tensor_core_precision"].get("finding"):
        return data["tensor_core_precision"]["finding"]
    if "hip_portability" in data and data["hip_portability"].get("finding"):
        return data["hip_portability"]["finding"]
    imported_collectives = data.get("imported_benchmarks", {})
    if imported_collectives.get("status") == "ran":
        best = imported_collectives.get("best_by_tool", [])
        winners = ", ".join(
            f"{row['tool']} {row['best_busbw_gbps']} GB/s at {row['best_message_bytes']} bytes"
            for row in best
        )
        return f"{imported_collectives.get('finding')} Best imported rows: {winners}."
    if "collective_model" in data and data["collective_model"].get("finding"):
        return data["collective_model"]["finding"]
    if "synthesis" in data and data["synthesis"].get("final_read"):
        return data["synthesis"]["final_read"]
    if "rows" in data and data["rows"]:
        first = data["rows"][0]
        return f"{len(data['rows'])} measured rows; first row: {first}"
    if "result" in data and isinstance(data["result"], dict):
        return text_blob(data["result"])[:240]
    if "boundary" in data:
        return data["boundary"]
    return text_blob(data)[:240]


def paper_lesson_links(paper: dict[str, Any], lessons: list[dict[str, Any]], profile: dict[str, Any]) -> list[dict[str, Any]]:
    paper_terms = tokens(
        [
            paper.get("title", ""),
            paper.get("primary_theme", ""),
            paper.get("problem", ""),
            paper.get("method", ""),
            paper.get("key_novelty", ""),
            paper.get("hardware_target", []),
            paper.get("technique_category", []),
            paper.get("workloads", []),
            paper.get("tags", []),
        ]
    )
    links = []
    for lesson in lessons:
        shared_topics = set(lesson.get("topics", [])).intersection(profile["lesson_topics"])
        shared_concepts = set(lesson.get("concepts", [])).intersection(profile["lesson_concepts"])
        lesson_terms = lesson.get("_link_terms") or tokens(
            [
                lesson.get("title", ""),
                lesson.get("topics", []),
                lesson.get("concepts", []),
                lesson.get("tools", []),
                lesson.get("exercise_candidates", []),
            ]
        )
        shared_terms = sorted(paper_terms.intersection(lesson_terms))
        score = 4 * len(shared_topics) + 5 * len(shared_concepts) + len(shared_terms)
        if score <= 0:
            continue
        links.append(
            {
                "index": lesson["index"],
                "title": lesson["title"],
                "url": lesson["url"],
                "matched_topics": sorted(shared_topics),
                "matched_concepts": sorted(shared_concepts),
                "matched_terms": shared_terms[:8],
                "score": score,
            }
        )
    return sorted(links, key=lambda row: (-row["score"], row["index"]))[:3]


def prepare_lesson_link_index(lessons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed = []
    for lesson in lessons:
        indexed.append(
            {
                **lesson,
                "_link_terms": tokens(
                    [
                        lesson.get("title", ""),
                        lesson.get("topics", []),
                        lesson.get("concepts", []),
                        lesson.get("tools", []),
                        lesson.get("exercise_candidates", []),
                    ]
                ),
            }
        )
    return indexed


def collect_papers(profile: dict[str, Any], lessons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(PAPER_ROOT.glob("*.json")):
        paper = read_json(path, {})
        score = paper_score(paper, profile)
        if score <= 0:
            continue
        linked_lessons = paper_lesson_links(paper, lessons, profile)
        rows.append(
            {
                "id": paper.get("id", path.stem),
                "title": paper.get("title", path.stem),
                "venue": paper.get("venue", ""),
                "theme": paper.get("primary_theme", ""),
                "confidence": paper.get("confidence", ""),
                "path": str(path.relative_to(REPO)),
                "linked_lessons": linked_lessons,
                "score": score,
            }
        )
    return sorted(rows, key=lambda row: (-row["score"], row["venue"], row["title"]))[:8]


def bridge_score(paper_terms: set[str], lesson: dict[str, Any]) -> tuple[int, list[str]]:
    lesson_terms = lesson.get("_link_terms") or tokens(
        [
            lesson.get("title", ""),
            lesson.get("topics", []),
            lesson.get("concepts", []),
            lesson.get("tools", []),
            lesson.get("exercise_candidates", []),
        ]
    )
    shared_terms = sorted(paper_terms.intersection(lesson_terms))
    topic_bonus = 4 * len(set(lesson.get("topics", [])).intersection(paper_terms))
    concept_bonus = 5 * len(set(lesson.get("concepts", [])).intersection(paper_terms))
    return len(shared_terms) + topic_bonus + concept_bonus, shared_terms


def gpu_relevant_paper(paper: dict[str, Any]) -> bool:
    blob = text_blob(
        [
            paper.get("title", ""),
            paper.get("primary_theme", ""),
            paper.get("problem", ""),
            paper.get("method", ""),
            paper.get("hardware_target", []),
            paper.get("technique_category", []),
            paper.get("workloads", []),
            paper.get("tags", []),
        ]
    ).lower()
    return any(term in blob for term in ("gpu", "llm", "attention", "inference", "training", "accelerator", "cuda", "hbm", "tensor"))


def build_lesson_corpus_bridges(lessons: list[dict[str, Any]], profiles: list[dict[str, Any]]) -> dict[str, Any]:
    lesson_by_index = {lesson["index"]: lesson for lesson in lessons}
    paper_rows = []
    lesson_links: dict[int, list[dict[str, Any]]] = defaultdict(list)
    profile_by_paper: dict[str, set[str]] = defaultdict(set)
    for profile in profiles:
        for paper in profile.get("related_papers", []):
            profile_by_paper[paper["id"]].add(profile["id"])

    for path in sorted(PAPER_ROOT.glob("*.json")):
        paper = read_json(path, {})
        if not gpu_relevant_paper(paper):
            continue
        paper_terms = tokens(
            [
                paper.get("title", ""),
                paper.get("primary_theme", ""),
                paper.get("problem", ""),
                paper.get("method", ""),
                paper.get("key_novelty", ""),
                paper.get("hardware_target", []),
                paper.get("technique_category", []),
                paper.get("workloads", []),
                paper.get("tags", []),
            ]
        )
        links = []
        for lesson in lessons:
            score, shared_terms = bridge_score(paper_terms, lesson)
            if score <= 0:
                continue
            links.append(
                {
                    "index": lesson["index"],
                    "title": lesson["title"],
                    "url": lesson["url"],
                    "topics": lesson.get("topics", [])[:6],
                    "concepts": lesson.get("concepts", [])[:6],
                    "matched_terms": shared_terms[:10],
                    "score": score,
                }
            )
        links = sorted(links, key=lambda row: (-row["score"], row["index"]))[:6]
        if not links:
            continue
        record = {
            "id": paper.get("id", path.stem),
            "title": paper.get("title", path.stem),
            "venue": paper.get("venue", ""),
            "theme": paper.get("primary_theme", ""),
            "confidence": paper.get("confidence", ""),
            "path": str(path.relative_to(REPO)),
            "profile_ids": sorted(profile_by_paper.get(paper.get("id", path.stem), set())),
            "linked_lessons": links,
        }
        paper_rows.append(record)
        for link in links:
            lesson_links[link["index"]].append(
                {
                    "paper_id": record["id"],
                    "title": record["title"],
                    "venue": record["venue"],
                    "theme": record["theme"],
                    "path": record["path"],
                    "matched_terms": link["matched_terms"],
                    "score": link["score"],
                }
            )

    lesson_rows = []
    for lesson_index, rows in sorted(lesson_links.items()):
        lesson = lesson_by_index.get(lesson_index, {})
        ranked = sorted(rows, key=lambda row: (-row["score"], row["venue"], row["title"]))[:10]
        lesson_rows.append(
            {
                "index": lesson_index,
                "title": lesson.get("title", ""),
                "url": lesson.get("url", ""),
                "topics": lesson.get("topics", [])[:6],
                "concepts": lesson.get("concepts", [])[:6],
                "paper_count": len(rows),
                "top_papers": ranked,
            }
        )

    return {
        "generated_at": now(),
        "paper_count": len(paper_rows),
        "lesson_count": len(lesson_rows),
        "link_count": sum(len(row["linked_lessons"]) for row in paper_rows),
        "papers": sorted(paper_rows, key=lambda row: (row["venue"], row["title"])),
        "lessons": sorted(lesson_rows, key=lambda row: (-row["paper_count"], row["index"])),
    }


def build_profile(profile: dict[str, Any], lessons: list[dict[str, Any]], labs: list[dict[str, Any]]) -> dict[str, Any]:
    lesson_rows = [
        {
            "index": lesson["index"],
            "title": lesson["title"],
            "url": lesson["url"],
            "topics": lesson.get("topics", []),
            "concepts": lesson.get("concepts", []),
            "exercise_candidates": lesson.get("exercise_candidates", []),
            "score": score,
        }
        for lesson in lessons
        if (score := lesson_score(lesson, profile)) > 0
    ]
    lab_rows = [
        {
            "id": lab["id"],
            "title": lab["title"],
            "status": lab.get("status", "planned"),
            "implemented_as": lab.get("implemented_as"),
            "deliverable": lab.get("deliverable", ""),
            "score": score,
        }
        for lab in labs
        if (score := lab_score(lab, profile)) > 0
    ]
    ranked_lessons = sorted(lesson_rows, key=lambda row: (-row["score"], row["index"]))[:10]
    ranked_labs = sorted(lab_rows, key=lambda row: (-row["score"], row["status"] != "implemented", row["id"]))[:6]
    measurements = collect_measurements(profile)
    tutorial_sources = collect_tutorial_sources(profile)
    papers = collect_papers(profile, lessons)
    return {
        "id": profile["id"],
        "label": profile["label"],
        "diagnosis": diagnosis_for(profile["id"]),
        "recommended_lessons": ranked_lessons,
        "recommended_labs": ranked_labs,
        "latest_measurements": measurements,
        "related_papers": papers,
        "tutorial_sources": tutorial_sources,
        "exercise_path": build_exercise_path(profile, ranked_lessons, ranked_labs, measurements, tutorial_sources, papers),
        "next_action": next_action(ranked_labs, measurements),
    }


def diagnosis_for(profile_id: str) -> str:
    table = {
        "memory-bandwidth": "Suspect memory layout, HBM bandwidth, KV-cache growth, or avoidable materialization before changing math.",
        "profiling-roofline": "Suspect the next optimization is unclear until counters are mapped to memory, compute, synchronization, launch, or communication limits.",
        "warp-synchronization": "Suspect synchronization shape, block partials, divergent work, or reduction/scan dependency structure.",
        "triton-autotune": "Suspect block sizes, masks, fusion boundaries, or compiler-generated kernel choices.",
        "tensor-core-cutlass": "Suspect missing Tensor Core eligibility, low-precision numerical drift, layout mismatch, or missing CUTLASS/CuTe production kernel coverage.",
        "rocm-hip-portability": "Suspect CUDA-specific runtime calls, warp-size assumptions, WMMA/Tensor Core dependencies, or missing ROCm compiler/runtime support.",
        "pytorch-compiler-fusion": "Suspect graph breaks, unsupported Python control flow, missed fusion, or backend-generated kernels that need inspection.",
        "attention-serving": "Suspect prefill/decode split, KV-cache allocation, batching policy, prefix reuse, or attention materialization.",
        "serving-scheduler": "Suspect batching policy, chunked prefill, prefix-cache reuse, admission control, or SLA-driven decode scheduling.",
        "quantized-numerics": "Suspect memory savings versus numerical drift, dequantization overhead, or unsupported low-precision kernels.",
        "distributed-communication": "Suspect collective latency, bandwidth regime, topology, NCCL/NVSHMEM runtime readiness, or lack of multi-device parallelism.",
    }
    return table[profile_id]


def next_action(labs: list[dict[str, Any]], measurements: list[dict[str, Any]]) -> str:
    if labs:
        top = labs[0]
        if top["status"] == "implemented":
            return f"Run {top['implemented_as']} and compare its latest artifact against the recommended lessons."
        implemented = next((lab for lab in labs if lab["status"] == "implemented"), None)
        fallback = f" Existing fallback: run {implemented['implemented_as']} for adjacent evidence." if implemented else ""
        return f"Implement {top['id']} next; no implemented lab currently owns this bottleneck class.{fallback}"
    if measurements:
        return f"Inspect {measurements[0]['path']} and add a dedicated lab for this bottleneck class."
    return "Add a lab and measurement artifact for this bottleneck class."


def build() -> None:
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    SITE.mkdir(parents=True, exist_ok=True)
    curriculum = read_json(CURRICULUM, {})
    curriculum_graph = read_json(CURRICULUM_GRAPH, {})
    lessons = prepare_lesson_link_index(read_json(LESSON_INTELLIGENCE, []))
    labs = curriculum.get("proposed_labs", [])
    workbench = {
        "generated_at": now(),
        "inputs": {
            "lesson_intelligence": str(LESSON_INTELLIGENCE.relative_to(ROOT)),
            "curriculum": str(CURRICULUM.relative_to(ROOT)),
            "curriculum_graph": str(CURRICULUM_GRAPH.relative_to(ROOT)),
            "lab_root": str(LAB_ROOT.relative_to(REPO)),
            "paper_root": str(PAPER_ROOT.relative_to(REPO)),
            "tutorial_sources": str(TUTORIAL_SOURCES_JSON.relative_to(ROOT)),
            "tutorial_exercise_paths": str(TUTORIAL_EXERCISE_PATHS_JSON.relative_to(ROOT)),
            "lesson_corpus_bridges": str(LESSON_CORPUS_BRIDGES_JSON.relative_to(ROOT)),
            "latest_measurements": str(LATEST_MEASUREMENTS_JSON.relative_to(ROOT)),
        },
        "coverage": {
            "lessons": len(lessons),
            "labs": len(labs),
            "implemented_labs": sum(1 for lab in labs if lab.get("status") == "implemented"),
            "measurement_artifacts": len(list(LAB_ROOT.glob("**/out_*.json"))),
            "paper_json": len(list(PAPER_ROOT.glob("*.json"))),
            "tutorial_sources": len(TUTORIAL_SOURCES),
            "graph_nodes": curriculum_graph.get("node_count", 0),
            "graph_edges": curriculum_graph.get("edge_count", 0),
            "profile_count": len(PROFILES),
        },
        "profiles": [build_profile(profile, lessons, labs) for profile in PROFILES],
    }
    exercise_paths = [profile["exercise_path"] for profile in workbench["profiles"]]
    corpus_bridges = build_lesson_corpus_bridges(lessons, workbench["profiles"])
    latest_measurements = collect_latest_measurement_index()
    workbench["coverage"]["tutorial_exercise_paths"] = len(exercise_paths)
    workbench["coverage"]["lesson_corpus_bridge_papers"] = corpus_bridges["paper_count"]
    workbench["coverage"]["lesson_corpus_bridge_lessons"] = corpus_bridges["lesson_count"]
    workbench["coverage"]["lesson_corpus_bridge_links"] = corpus_bridges["link_count"]
    workbench["coverage"]["latest_measurement_index_rows"] = latest_measurements["artifact_count"]
    workbench["coverage"]["latest_measurement_correctness_passed"] = latest_measurements["passed_correctness"]
    workbench["coverage"]["latest_measurement_runtime_skips"] = latest_measurements["skipped_runtime_count"]
    TUTORIAL_SOURCES_JSON.write_text(json.dumps(TUTORIAL_SOURCES, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    TUTORIAL_EXERCISE_PATHS_JSON.write_text(json.dumps(exercise_paths, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    LESSON_CORPUS_BRIDGES_JSON.write_text(json.dumps(corpus_bridges, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    LATEST_MEASUREMENTS_JSON.write_text(json.dumps(latest_measurements, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(workbench, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_HTML.write_text(render_html(workbench), encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(ROOT)} and {OUT_HTML.relative_to(ROOT)}")


def esc(value: Any) -> str:
    return html.escape(str(value))


STYLE = """
:root{--bg:#0E1420;--bg2:#141D2C;--ink:#EAEEF4;--soft:#B4BFD0;--dim:#8493A8;--line:rgba(150,170,205,.14);--accent:#4FA8B8;--green:#74B87A;--amber:#E3A63A;--serif:"Iowan Old Style",Palatino,Georgia,serif;--sans:-apple-system,system-ui,"Segoe UI",Roboto,Arial,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.62}.wrap{max-width:1120px;margin:0 auto;padding:54px 24px 80px}
.kick,.meta{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}h1{font-family:var(--serif);font-size:clamp(34px,6vw,58px);line-height:1.05;margin:14px 0 0;color:#fff}
.dek{font-size:19px;color:var(--soft);max-width:78ch;margin-top:18px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:28px 0}
.card{background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:16px 18px}.card h2{font-family:var(--serif);font-size:23px;margin:0 0 6px;color:#fff}.card p{margin:0;color:var(--soft)}
section{padding:32px 0;border-top:1px solid var(--line)}h2{font-family:var(--serif);font-size:29px;margin:0 0 10px;color:#fff}h3{font-size:17px;margin:20px 0 8px;color:#fff}
table{width:100%;border-collapse:collapse;font-size:13px;margin:8px 0 18px}th,td{padding:8px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{font-family:var(--mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--dim)}td{color:var(--soft)}
a{color:var(--accent);text-decoration:none}.pill{display:inline-block;font-family:var(--mono);font-size:10.5px;color:var(--green);border:1px solid var(--line);border-radius:999px;padding:2px 7px;margin:2px}.status{color:var(--amber);font-family:var(--mono)}
.toolbar{display:grid;gap:12px;margin:26px 0 10px}.search{width:100%;background:#0C1119;border:1px solid var(--line);border-radius:8px;color:var(--ink);font:15px var(--sans);padding:12px 14px}.search:focus{outline:1px solid var(--accent)}
.chips{display:flex;gap:8px;flex-wrap:wrap}.chip{background:var(--bg2);border:1px solid var(--line);border-radius:999px;color:var(--soft);cursor:pointer;font:12px var(--mono);padding:7px 10px}.chip.active,.chip:hover{border-color:var(--accent);color:var(--ink)}
.hidden{display:none}.result-note{font-family:var(--mono);font-size:12px;color:var(--dim);margin-top:4px}.paper-links{font-size:12px;color:var(--dim);margin-top:5px}
"""


def pills(values: list[str]) -> str:
    return " ".join(f'<span class="pill">{esc(value)}</span>' for value in values[:5])


def render_html(workbench: dict[str, Any]) -> str:
    profile_sections = "\n".join(render_profile(profile) for profile in workbench["profiles"])
    coverage = workbench["coverage"]
    profile_chips = "\n".join(
        f'<button class="chip" type="button" data-profile="{esc(profile["id"])}">{esc(profile["id"])}</button>'
        for profile in workbench["profiles"]
    )
    data_json = json.dumps(workbench_payload(workbench), ensure_ascii=False).replace("</", "<\\/")
    return f"""<meta charset="utf-8">
<title>GPU Systems Workbench</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated GPU systems workbench</div>
  <h1>Pick a bottleneck, get the next measured move.</h1>
  <p class="dek">This page joins GPUMODE transcript intelligence, implemented labs, latest local
  measurement artifacts, and the AI-hardware paper corpus into bottleneck-specific recommendations.</p>
  <div class="grid">
    <div class="card"><h2>{esc(coverage["lessons"])}</h2><p>GPUMODE lesson records</p></div>
    <div class="card"><h2>{esc(coverage["implemented_labs"])} / {esc(coverage["labs"])}</h2><p>deep labs implemented</p></div>
    <div class="card"><h2>{esc(coverage["measurement_artifacts"])}</h2><p>local measurement artifacts</p></div>
    <div class="card"><h2>{esc(coverage["paper_json"])}</h2><p>paper JSON records scored</p></div>
  </div>
  <div class="toolbar">
    <input id="workbench-search" class="search" type="search" placeholder="Filter profiles, lessons, labs, papers, or measurements">
    <div class="chips"><button class="chip active" type="button" data-profile="all">all profiles</button>{profile_chips}</div>
    <div id="result-note" class="result-note"></div>
  </div>
  {profile_sections}
</div>
<script type="application/json" id="workbench-data">{data_json}</script>
<script>{INTERACTIVE_JS}</script>
"""


def workbench_payload(workbench: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": workbench["generated_at"],
        "coverage": workbench["coverage"],
        "profiles": [
            {
                "id": profile["id"],
                "label": profile["label"],
                "next_action": profile["next_action"],
                "labs": profile["recommended_labs"][:4],
                "lessons": profile["recommended_lessons"][:5],
                "measurements": profile["latest_measurements"][:4],
                "tutorial_sources": profile.get("tutorial_sources", [])[:4],
                "exercise_path": profile.get("exercise_path", {}),
                "papers": profile["related_papers"][:4],
            }
            for profile in workbench["profiles"]
        ],
    }


INTERACTIVE_JS = """
const data = JSON.parse(document.getElementById('workbench-data').textContent);
const search = document.getElementById('workbench-search');
const note = document.getElementById('result-note');
const chips = [...document.querySelectorAll('[data-profile]')];
const sections = [...document.querySelectorAll('section[data-profile]')];
let selected = 'all';
function applyFilter() {
  const query = search.value.trim().toLowerCase();
  let shown = 0;
  for (const section of sections) {
    const profileOk = selected === 'all' || section.dataset.profile === selected;
    const queryOk = !query || section.dataset.search.includes(query);
    const visible = profileOk && queryOk;
    section.classList.toggle('hidden', !visible);
    if (visible) shown += 1;
  }
  note.textContent = `${shown} of ${sections.length} bottleneck profiles shown`;
}
chips.forEach(chip => chip.addEventListener('click', () => {
  selected = chip.dataset.profile;
  chips.forEach(node => node.classList.toggle('active', node === chip));
  applyFilter();
}));
search.addEventListener('input', applyFilter);
applyFilter();
"""


def profile_search_text(profile: dict[str, Any]) -> str:
    parts: list[Any] = [
        profile["id"],
        profile["label"],
        profile["diagnosis"],
        profile["next_action"],
    ]
    for lab in profile["recommended_labs"]:
        parts.extend([lab["id"], lab["title"], lab.get("implemented_as", ""), lab.get("deliverable", "")])
    for lesson in profile["recommended_lessons"]:
        parts.extend([lesson["title"], lesson.get("topics", []), lesson.get("concepts", []), lesson.get("exercise_candidates", [])])
    for measurement in profile["latest_measurements"]:
        parts.extend([measurement["path"], measurement["session"], measurement.get("summary", "")])
    for paper in profile["related_papers"]:
        parts.extend([paper["title"], paper.get("venue", ""), paper.get("theme", ""), paper.get("confidence", "")])
    for source in profile.get("tutorial_sources", []):
        parts.extend([source["provider"], source["title"], source.get("focus_terms", []), source.get("why", "")])
    parts.extend(profile.get("exercise_path", {}).get("steps", []))
    parts.extend(profile.get("exercise_path", {}).get("success_checks", []))
    return " ".join(text_blob(part).lower() for part in parts)


def render_profile(profile: dict[str, Any]) -> str:
    searchable = profile_search_text(profile)
    bridge = f"bridge-{profile['id']}.html"
    return f"""
<section id="{esc(profile["id"])}" data-profile="{esc(profile["id"])}" data-search="{esc(searchable)}">
  <div class="meta">{esc(profile["id"])}</div>
  <h2><a href="{esc(bridge)}">{esc(profile["label"])}</a></h2>
  <p>{esc(profile["diagnosis"])}</p>
  <div class="card"><strong>Next action:</strong> {esc(profile["next_action"])}</div>
  <h3>Recommended GPUMODE Lessons</h3>
  <table>
    <tr><th>#</th><th>lesson</th><th>topics</th><th>concepts</th><th>exercise candidates</th></tr>
    {lesson_rows(profile["recommended_lessons"])}
  </table>
  <h3>Runnable Labs</h3>
  <table>
    <tr><th>lab</th><th>status</th><th>implemented as</th><th>deliverable</th></tr>
    {lab_rows(profile["recommended_labs"])}
  </table>
  <h3>Latest Local Measurements</h3>
  <table>
    <tr><th>artifact</th><th>session</th><th>status</th><th>CUDA</th><th>summary</th></tr>
    {measurement_rows(profile["latest_measurements"])}
  </table>
  <h3>External Tutorial Sources</h3>
  <table>
    <tr><th>provider</th><th>source</th><th>focus</th><th>why it belongs here</th></tr>
    {tutorial_rows(profile["tutorial_sources"])}
  </table>
  <h3>End-To-End Exercise Path</h3>
  {exercise_path_html(profile["exercise_path"])}
  <h3>Related Corpus Papers</h3>
  <table>
    <tr><th>venue</th><th>paper</th><th>theme</th><th>confidence</th><th>lesson links</th></tr>
    {paper_rows(profile["related_papers"])}
  </table>
</section>
"""


def lesson_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="5">No lesson recommendations generated.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['index'])}</td>"
        f'<td><a href="{esc(row["url"])}">{esc(row["title"])}</a></td>'
        f"<td>{pills(row['topics'])}</td>"
        f"<td>{esc(', '.join(row['concepts'][:5]))}</td>"
        f"<td>{esc('; '.join(row['exercise_candidates'][:2]))}</td>"
        "</tr>"
        for row in rows
    )


def lab_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="4">No lab recommendations generated.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['id'])}</td>"
        f'<td class="status">{esc(row["status"])}</td>'
        f"<td>{esc(row.get('implemented_as') or '')}</td>"
        f"<td>{esc(row['deliverable'])}</td>"
        "</tr>"
        for row in rows
    )


def measurement_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="5">No matching measurement artifacts found.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['path'])}</td>"
        f"<td>{esc(row['session'])}</td>"
        f"<td>{esc(row['status'])}</td>"
        f"<td>{esc(row.get('cuda_status') or '')}</td>"
        f"<td>{esc(row['summary'])}</td>"
        "</tr>"
        for row in rows
    )


def tutorial_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="4">No tutorial sources matched.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['provider'])}</td>"
        f'<td><a href="{esc(row["url"])}">{esc(row["title"])}</a></td>'
        f"<td>{pills(row.get('focus_terms', []))}</td>"
        f"<td>{esc(row['why'])}</td>"
        "</tr>"
        for row in rows
    )


def exercise_path_html(path: dict[str, Any]) -> str:
    if not path:
        return '<div class="card">No exercise path generated.</div>'
    steps = "".join(f"<li>{esc(step)}</li>" for step in path.get("steps", []))
    checks = "".join(f"<li>{esc(check)}</li>" for check in path.get("success_checks", []))
    lab = path.get("lab", {})
    measurement = path.get("measurement", {})
    source = path.get("source_reading", {})
    return f"""
  <div class="card">
    <strong>{esc(path.get("title", ""))}</strong>
    <p>{esc(path.get("objective", ""))}</p>
    <p><span class="status">source</span> <a href="{esc(source.get("url", ""))}">{esc(source.get("provider", ""))}: {esc(source.get("title", ""))}</a></p>
    <p><span class="status">run</span> {esc(lab.get("command", ""))}</p>
    <p><span class="status">artifact</span> {esc(measurement.get("path", ""))}</p>
    <h4>Steps</h4>
    <ol>{steps}</ol>
    <h4>Success Checks</h4>
    <ul>{checks}</ul>
  </div>
"""


def paper_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="5">No related corpus papers found.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['venue'])}</td>"
        f"<td>{esc(row['title'])}</td>"
        f"<td>{esc(row['theme'])}</td>"
        f"<td>{esc(row['confidence'])}</td>"
        f"<td>{paper_lesson_cells(row.get('linked_lessons', []))}</td>"
        "</tr>"
        for row in rows
    )


def paper_lesson_cells(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    return "<br>".join(
        f'<a href="{esc(row["url"])}">#{esc(row["index"])} {esc(row["title"])}</a>'
        f'<div class="paper-links">{esc(", ".join(row.get("matched_concepts") or row.get("matched_topics") or row.get("matched_terms", [])))}</div>'
        for row in rows
    )


if __name__ == "__main__":
    build()
