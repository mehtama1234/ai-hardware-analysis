#!/usr/bin/env python3
"""Classify GPUMODE lessons and propose deeper runnable labs."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "raw-material" / "youtube" / "transcript-index.json"
ANALYSIS = ROOT / "analysis"
CURRICULUM = ANALYSIS / "gpumode-curriculum.json"
TOPIC_MAP = ANALYSIS / "topic-map.json"
CURRICULUM_GRAPH = ANALYSIS / "curriculum-graph.json"
LESSON_INTELLIGENCE = ANALYSIS / "lesson-intelligence.json"

TOPICS = {
    "cuda": ["cuda", "kernel", "warp", "block", "thread", "shared memory", "coalesc", "occupancy"],
    "triton": ["triton", "tl.", "autotun", "program id", "block pointer"],
    "pytorch-compiler": ["torch.compile", "inductor", "dynamo", "aot", "fx graph", "graph break"],
    "profiling": ["nsight", "profiler", "profile", "trace", "roofline", "benchmark", "latency"],
    "attention": ["attention", "flashattention", "softmax", "kv cache", "pagedattention", "prefill", "decode"],
    "quantization": ["quant", "int8", "int4", "fp8", "mxfp", "bitsandbytes", "qlora"],
    "serving": ["vllm", "serving", "inference", "batching", "scheduler", "throughput", "tgi"],
    "hardware": ["h100", "a100", "gpu architecture", "tensor core", "sm", "memory hierarchy", "nvlink"],
    "distributed": ["distributed", "all-reduce", "collective", "communication", "parallelism", "sharding"],
    "cutlass": ["cutlass", "cute", "wmma", "mma", "tensor core"],
}

CONCEPTS = {
    "memory coalescing": ["coalesc", "contiguous", "strided", "global memory", "memory access"],
    "shared memory tiling": ["shared memory", "tile", "tiling", "smem"],
    "warp execution": ["warp", "lane", "shuffle", "divergence", "SIMT"],
    "occupancy": ["occupancy", "register pressure", "active warps", "resident"],
    "tensor cores": ["tensor core", "wmma", "mma", "wgmma", "tcgen"],
    "online softmax": ["online softmax", "flash attention", "flashattention", "softmax"],
    "kv cache": ["kv cache", "pagedattention", "paged attention", "prefill", "decode"],
    "kernel fusion": ["fusion", "fused", "megakernel", "epilogue"],
    "autotuning": ["autotun", "search", "configuration", "sweep"],
    "collectives": ["nccl", "all-reduce", "allreduce", "collective", "nvshmem"],
    "quantized numerics": ["int8", "int4", "fp8", "nvfp4", "mxfp", "quant"],
    "compiler lowering": ["inductor", "dynamo", "mlir", "tvm", "tir", "lowering"],
    "profiling workflow": ["nsight", "profiler", "trace", "counter", "timeline"],
}

TOOLS = {
    "CUDA": ["cuda", "nvcc", ".cu"],
    "Triton": ["triton", "tl."],
    "PyTorch": ["pytorch", "torch"],
    "torch.compile": ["torch.compile", "inductor", "dynamo"],
    "CUTLASS/CuTe": ["cutlass", "cute"],
    "Nsight": ["nsight"],
    "NCCL": ["nccl"],
    "NVSHMEM": ["nvshmem"],
    "vLLM": ["vllm"],
    "ROCm/HIP": ["rocm", "hip"],
    "JAX": ["jax", "xla"],
    "TVM": ["tvm", "tir"],
}

PAPER_REPO_PATTERNS = [
    r"https?://github\.com/[^\s)>,]+",
    r"https?://arxiv\.org/[^\s)>,]+",
    r"https?://openreview\.net/[^\s)>,]+",
    r"flashattention",
    r"cutlass",
    r"vllm",
    r"triton",
    r"pytorch",
]

LABS = [
    {
        "id": "gpumode-lab-01-coalescing",
        "title": "CUDA memory coalescing microscope",
        "topics": ["cuda", "profiling"],
        "deliverable": "CUDA and PyTorch benchmark comparing contiguous, strided, and gathered loads.",
        "extends": "gpu-kernels-serving-lab/03-cuda-vector-reduce",
        "status": "implemented",
        "implemented_as": "gpu-kernels-serving-lab/15-gpumode-coalescing",
    },
    {
        "id": "gpumode-lab-02-warp-reductions",
        "title": "Warp reductions and scans",
        "topics": ["cuda", "hardware"],
        "deliverable": "Shared-memory vs warp-shuffle reductions with correctness and timing artifacts.",
        "extends": "gpu-kernels-serving-lab/03-cuda-vector-reduce",
        "status": "implemented",
        "implemented_as": "gpu-kernels-serving-lab/16-gpumode-warp-reductions",
    },
    {
        "id": "gpumode-lab-03-triton-autotune",
        "title": "Triton matmul autotuning workbench",
        "topics": ["triton", "profiling"],
        "deliverable": "Autotuned Triton matmul with block-size sweep and generated performance table.",
        "extends": "gpu-kernels-serving-lab/06-triton-matmul",
        "status": "implemented",
        "implemented_as": "gpu-kernels-serving-lab/17-gpumode-triton-autotune",
    },
    {
        "id": "gpumode-lab-04-online-softmax",
        "title": "FlashAttention-style online softmax",
        "topics": ["attention", "triton", "cuda"],
        "deliverable": "Naive attention, online softmax, and fused Triton comparison.",
        "extends": "gpu-kernels-serving-lab/05-cuda-tiny-attention",
        "status": "implemented",
        "implemented_as": "gpu-kernels-serving-lab/18-gpumode-online-softmax",
    },
    {
        "id": "gpumode-lab-05-torch-compile",
        "title": "torch.compile fusion and graph-break lab",
        "topics": ["pytorch-compiler", "triton"],
        "deliverable": "Before/after graph and benchmark showing when compiler fusion helps.",
        "extends": "gpu-kernels-serving-lab/01-hf-baseline",
        "status": "implemented",
        "implemented_as": "gpu-kernels-serving-lab/19-gpumode-torch-compile",
    },
    {
        "id": "gpumode-lab-06-vllm-scheduler",
        "title": "vLLM scheduler and KV-cache pressure lab",
        "topics": ["serving", "attention", "profiling"],
        "deliverable": "Request generator measuring TTFT, TPOT, batching, and prefix-cache behavior.",
        "extends": "gpu-kernels-serving-lab/09-vllm-serving",
        "status": "implemented",
        "implemented_as": "gpu-kernels-serving-lab/20-gpumode-vllm-scheduler",
    },
    {
        "id": "gpumode-lab-07-quantized-kernels",
        "title": "Quantized matmul kernel ladder",
        "topics": ["quantization", "triton", "cuda"],
        "deliverable": "fp16/int8/int4 weight-only matmul with error and throughput artifacts.",
        "extends": "gpu-kernels-serving-lab/08-quantized-inference",
        "status": "implemented",
        "implemented_as": "gpu-kernels-serving-lab/21-gpumode-quantized-kernels",
    },
    {
        "id": "gpumode-lab-08-nsight-to-roofline",
        "title": "Nsight-to-roofline workflow",
        "topics": ["profiling", "hardware"],
        "deliverable": "Profiler trace checklist mapping counters to compute/memory/launch bottlenecks.",
        "extends": "gpu-kernels-serving-lab/02-roofline",
        "status": "implemented",
        "implemented_as": "gpu-kernels-serving-lab/22-gpumode-nsight-roofline",
    },
    {
        "id": "gpumode-lab-09-shared-memory-gemm",
        "title": "Shared-memory tiled GEMM microscope",
        "topics": ["cuda", "hardware", "profiling", "cutlass"],
        "deliverable": "Naive vs shared-memory tiled GEMM with traffic, arithmetic-intensity, correctness, and CUDA source artifacts.",
        "extends": "gpu-kernels-serving-lab/04-cuda-tiled-matmul",
        "status": "implemented",
        "implemented_as": "gpu-kernels-serving-lab/23-gpumode-shared-memory-gemm",
    },
    {
        "id": "gpumode-lab-10-tensor-core-cutlass",
        "title": "Tensor Core and CUTLASS matmul readiness",
        "topics": ["cuda", "hardware", "cutlass", "quantization"],
        "deliverable": "WMMA Tensor Core source, MMA tile eligibility model, low-precision drift measurements, and CUTLASS readiness checks.",
        "extends": "gpu-kernels-serving-lab/23-gpumode-shared-memory-gemm",
        "status": "implemented",
        "implemented_as": "gpu-kernels-serving-lab/24-gpumode-tensor-core-cutlass",
    },
    {
        "id": "gpumode-lab-11-rocm-hip-portability",
        "title": "ROCm/HIP portability workbench",
        "topics": ["cuda", "hardware", "distributed"],
        "deliverable": "CUDA-to-HIP translation report, HIP source kernels, CPU semantic checks, and ROCm compile/run readiness.",
        "extends": "gpu-kernels-serving-lab/11-rocm-hip-port",
        "status": "implemented",
        "implemented_as": "gpu-kernels-serving-lab/25-gpumode-rocm-hip-portability",
    },
    {
        "id": "gpumode-lab-12-distributed-communication",
        "title": "Distributed communication and collectives workbench",
        "topics": ["distributed", "profiling", "hardware"],
        "deliverable": "All-reduce/NVSHMEM-style communication model, local all-reduce semantic check, and NCCL/NVSHMEM readiness artifact.",
        "extends": "gpu-kernels-serving-lab/12-jax-scaling-practicum",
        "status": "implemented",
        "implemented_as": "gpu-kernels-serving-lab/26-gpumode-distributed-communication",
    },
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_index() -> list[dict[str, Any]]:
    if not INDEX.exists():
        return []
    return json.loads(INDEX.read_text(encoding="utf-8"))


def text_for(row: dict[str, Any]) -> str:
    parts = [row.get("title") or ""]
    clean = row.get("clean_txt")
    if clean:
        path = ROOT / clean
        if path.exists():
            parts.append(path.read_text(encoding="utf-8", errors="ignore")[:12000])
    return "\n".join(parts).lower()


def text_original(row: dict[str, Any]) -> str:
    parts = [row.get("title") or ""]
    clean = row.get("clean_txt")
    if clean:
        path = ROOT / clean
        if path.exists():
            parts.append(path.read_text(encoding="utf-8", errors="ignore")[:24000])
    return "\n".join(parts)


def classify(row: dict[str, Any]) -> list[str]:
    text = text_for(row)
    hits = []
    for topic, needles in TOPICS.items():
        if any(needle in text for needle in needles):
            hits.append(topic)
    return hits or ["uncategorized"]


def match_terms(text: str, table: dict[str, list[str]]) -> list[str]:
    lower = text.lower()
    return [name for name, needles in table.items() if any(needle.lower() in lower for needle in needles)]


def extract_mentions(text: str) -> list[str]:
    hits: list[str] = []
    lower = text.lower()
    for pattern in PAPER_REPO_PATTERNS:
        for match in re.finditer(pattern, lower):
            value = match.group(0).rstrip(".,;:")
            if value not in hits:
                hits.append(value)
    return hits[:24]


def prerequisite_signals(topics: list[str], concepts: list[str]) -> list[str]:
    prereqs: list[str] = []
    if "triton" in topics:
        prereqs.extend(["Python tensor indexing", "GPU program/block model", "memory coalescing"])
    if "cuda" in topics:
        prereqs.extend(["C/C++ basics", "thread/block indexing", "host-device memory movement"])
    if "cutlass" in topics or "tensor cores" in concepts:
        prereqs.extend(["tiled matmul", "shared memory", "CUDA templates"])
    if "attention" in topics:
        prereqs.extend(["matrix multiplication", "softmax", "prefill vs decode"])
    if "serving" in topics:
        prereqs.extend(["LLM generation loop", "KV cache", "batching"])
    if "distributed" in topics:
        prereqs.extend(["collectives", "latency vs bandwidth", "multi-GPU topology"])
    if "pytorch-compiler" in topics:
        prereqs.extend(["PyTorch eager execution", "FX graphs", "kernel fusion"])
    deduped = []
    for item in prereqs:
        if item not in deduped:
            deduped.append(item)
    return deduped[:10]


def exercise_candidates(topics: list[str], concepts: list[str]) -> list[str]:
    exercises = []
    if "memory coalescing" in concepts:
        exercises.append("benchmark contiguous, strided, and gathered loads")
    if "shared memory tiling" in concepts:
        exercises.append("implement naive vs tiled matrix multiplication")
    if "warp execution" in concepts:
        exercises.append("compare shared-memory reduction with warp-shuffle reduction")
    if "online softmax" in concepts:
        exercises.append("implement numerically stable online softmax and compare to materialized softmax")
    if "kv cache" in concepts:
        exercises.append("simulate prefill/decode KV-cache memory growth")
    if "kernel fusion" in concepts:
        exercises.append("fuse bias, activation, and normalization into one measured path")
    if "autotuning" in concepts:
        exercises.append("sweep block sizes and record the winning kernel configuration")
    if "collectives" in concepts:
        exercises.append("model all-reduce latency and bandwidth regimes")
    if "quantized numerics" in concepts:
        exercises.append("measure int8/int4/fp8-style quantization error and memory savings")
    if "profiling workflow" in concepts:
        exercises.append("capture a profiler trace and classify bottleneck type")
    if not exercises and "cuda" in topics:
        exercises.append("write a correctness-tested CUDA kernel with CPU fallback")
    if not exercises and "triton" in topics:
        exercises.append("write a correctness-tested Triton kernel with skip artifact")
    if not exercises:
        exercises.append("turn the lesson into a measurement-backed concept page")
    return exercises[:6]


def lab_readiness(topics: list[str], concepts: list[str]) -> str:
    if {"cuda", "profiling"}.issubset(topics) or "memory coalescing" in concepts:
        return "ready-for-coalescing-lab"
    if "attention" in topics and ("online softmax" in concepts or "kv cache" in concepts):
        return "ready-for-attention-lab"
    if "triton" in topics and "autotuning" in concepts:
        return "ready-for-triton-autotune-lab"
    if "serving" in topics and "kv cache" in concepts:
        return "ready-for-serving-lab"
    if "cutlass" in topics or "tensor cores" in concepts:
        return "needs-gpu-for-tensor-core-lab"
    return "needs-human-triage"


def build_intelligence(row: dict[str, Any], topics: list[str]) -> dict[str, Any]:
    original = text_original(row)
    concepts = match_terms(original, CONCEPTS)
    tools = match_terms(original, TOOLS)
    return {
        "id": row["id"],
        "index": row["index"],
        "title": row["title"],
        "url": row["url"],
        "transcript_status": row["transcript_status"],
        "word_count": row["word_count"],
        "topics": topics,
        "concepts": concepts,
        "tools": tools,
        "prerequisites": prerequisite_signals(topics, concepts),
        "paper_or_repo_mentions": extract_mentions(original),
        "exercise_candidates": exercise_candidates(topics, concepts),
        "lab_readiness": lab_readiness(topics, concepts),
    }


def extract_lesson_number(title: str) -> int | None:
    match = re.search(r"(?:lecture|lesson)\s*#?\s*(\d+)", title, re.IGNORECASE)
    return int(match.group(1)) if match else None


def slug(kind: str, value: Any) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return f"{kind}:{text or 'unknown'}"


def add_node(nodes: dict[str, dict[str, Any]], node_id: str, kind: str, label: str, **extra: Any) -> None:
    if node_id not in nodes:
        nodes[node_id] = {"id": node_id, "kind": kind, "label": label, **extra}


def add_edge(edges: list[dict[str, Any]], seen: set[tuple[str, str, str]], src: str, dst: str, relation: str, **extra: Any) -> None:
    key = (src, dst, relation)
    if key in seen:
        return
    seen.add(key)
    edges.append({"source": src, "target": dst, "relation": relation, **extra})


def build_curriculum_graph(lessons: list[dict[str, Any]], topic_lessons: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str]] = set()
    prereq_topic_counts: dict[tuple[str, str], int] = defaultdict(int)
    topic_pair_counts: dict[tuple[str, str], int] = defaultdict(int)

    for topic, rows in topic_lessons.items():
        add_node(nodes, slug("topic", topic), "topic", topic, lesson_count=len(rows), keywords=TOPICS.get(topic, []))

    for lab in LABS:
        lab_id = slug("lab", lab["id"])
        add_node(nodes, lab_id, "lab", lab["title"], lab_id=lab["id"], status=lab["status"], implemented_as=lab.get("implemented_as", ""))
        for topic in lab.get("topics", []):
            topic_id = slug("topic", topic)
            add_edge(edges, seen_edges, topic_id, lab_id, "has_runnable_lab", lab_id=lab["id"])

    for lesson in lessons:
        lesson_id = slug("lesson", lesson["index"])
        add_node(
            nodes,
            lesson_id,
            "lesson",
            lesson["title"],
            index=lesson["index"],
            url=lesson["url"],
            transcript_status=lesson["transcript_status"],
        )
        topics = lesson.get("topics", [])
        for topic in topics:
            topic_id = slug("topic", topic)
            add_edge(edges, seen_edges, lesson_id, topic_id, "covers_topic")
        for left in topics:
            for right in topics:
                if left < right:
                    topic_pair_counts[(left, right)] += 1
        for concept in lesson.get("concepts", []):
            concept_id = slug("concept", concept)
            add_node(nodes, concept_id, "concept", concept)
            add_edge(edges, seen_edges, lesson_id, concept_id, "teaches_concept")
            for topic in topics:
                add_edge(edges, seen_edges, slug("topic", topic), concept_id, "includes_concept")
        for prereq in lesson.get("prerequisites", []):
            prereq_id = slug("prerequisite", prereq)
            add_node(nodes, prereq_id, "prerequisite", prereq)
            add_edge(edges, seen_edges, prereq_id, lesson_id, "prerequisite_for")
            for topic in topics:
                prereq_topic_counts[(prereq, topic)] += 1
        for lab_id in lesson.get("candidate_lab_links", []):
            add_edge(edges, seen_edges, lesson_id, slug("lab", lab_id), "candidate_lab", lab_id=lab_id)

    for (prereq, topic), count in sorted(prereq_topic_counts.items()):
        if count >= 3:
            add_edge(
                edges,
                seen_edges,
                slug("prerequisite", prereq),
                slug("topic", topic),
                "prepares_topic",
                support_count=count,
            )

    for (left, right), count in sorted(topic_pair_counts.items()):
        if count >= 5:
            add_edge(
                edges,
                seen_edges,
                slug("topic", left),
                slug("topic", right),
                "co_occurs_with",
                support_count=count,
            )

    topic_order = []
    for topic in sorted(topic_lessons):
        prereq_support = sum(count for (prereq, candidate), count in prereq_topic_counts.items() if candidate == topic)
        implemented_labs = [
            lab["id"]
            for lab in LABS
            if lab.get("status") == "implemented" and topic in lab.get("topics", [])
        ]
        topic_order.append(
            {
                "topic": topic,
                "lesson_count": len(topic_lessons[topic]),
                "prerequisite_signal_count": prereq_support,
                "implemented_labs": implemented_labs,
                "order_score": prereq_support + 4 * len(implemented_labs) + len(topic_lessons[topic]),
            }
        )

    return {
        "generated_at": now(),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": sorted(nodes.values(), key=lambda row: (row["kind"], row["id"])),
        "edges": sorted(edges, key=lambda row: (row["relation"], row["source"], row["target"])),
        "practical_topic_order": sorted(topic_order, key=lambda row: (-row["order_score"], row["topic"])),
    }


def build() -> None:
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    lessons = []
    intelligence_records = []
    topic_lessons: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in load_index():
        topics = classify(row)
        intelligence = build_intelligence(row, topics)
        lesson = {
            **row,
            "lesson_number": extract_lesson_number(row.get("title") or ""),
            "topics": topics,
            "concepts": intelligence["concepts"],
            "tools": intelligence["tools"],
            "prerequisites": intelligence["prerequisites"],
            "exercise_candidates": intelligence["exercise_candidates"],
            "lab_readiness": intelligence["lab_readiness"],
            "candidate_lab_links": [lab["id"] for lab in LABS if set(lab["topics"]).intersection(topics)],
        }
        lessons.append(lesson)
        intelligence_records.append(intelligence)
        for topic in topics:
            topic_lessons[topic].append(
                {
                    "index": lesson["index"],
                    "title": lesson["title"],
                    "url": lesson["url"],
                    "transcript_status": lesson["transcript_status"],
                }
            )

    counts = Counter(topic for lesson in lessons for topic in lesson["topics"])
    curriculum = {
        "generated_at": now(),
        "source_index": str(INDEX.relative_to(ROOT)),
        "lesson_count": len(lessons),
        "transcript_count": sum(1 for lesson in lessons if lesson["transcript_status"] == "available"),
        "topic_counts": dict(sorted(counts.items())),
        "lab_readiness_counts": dict(sorted(Counter(row["lab_readiness"] for row in intelligence_records).items())),
        "lessons": lessons,
        "lesson_intelligence": str(LESSON_INTELLIGENCE.relative_to(ROOT)),
        "proposed_labs": LABS,
        "next_build_order": [lab["id"] for lab in LABS],
    }
    topic_map = {
        "generated_at": now(),
        "topics": {
            topic: {
                "keywords": TOPICS.get(topic, []),
                "lesson_count": len(rows),
                "lessons": rows,
            }
            for topic, rows in sorted(topic_lessons.items())
        },
    }
    CURRICULUM.write_text(json.dumps(curriculum, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    TOPIC_MAP.write_text(json.dumps(topic_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    CURRICULUM_GRAPH.write_text(
        json.dumps(build_curriculum_graph(lessons, topic_lessons), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    LESSON_INTELLIGENCE.write_text(json.dumps(intelligence_records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {CURRICULUM.relative_to(ROOT)} with {len(lessons)} lessons")


if __name__ == "__main__":
    build()
