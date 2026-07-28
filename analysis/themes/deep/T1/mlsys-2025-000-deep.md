# FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving

**Venue:** MLSYS 2025 · **Theme:** Hardware-Fused Attention Kernels

## What It Does

LLM inference serving requires attention kernels that simultaneously handle heterogeneous KV-cache storage layouts (ragged, paged, tree-structured), diverse attention variants (GQA, MLA, sliding-window), and dynamic request batching, while remaining compatible with static CUDAGraph capture.

Existing attention kernels (FlashAttention, Triton-based backends) are optimized for a single storage format and static batch shapes; adapting them to production serving workloads with shared prefixes, paged memory, and mixed request types requires significant rewriting and yields suboptimal memory access and load imbalance.

FlashInfer introduces: (1) Block-Sparse Row (BSR) format as a unified KV-cache representation that encodes ragged, paged, and prefix-tree layouts via a single sparse block structure; (2) composable format decomposition that splits shared-prefix attention from unique-suffix attention and merges partial softmax accumulators; (3) a JIT compiler that instantiates CUDA attention templates per attention variant at first use, reusing compiled binaries across requests; (4) a load-balanced scheduler that uses a priority queue to assign work tiles to thread blocks while preserving CUDAGraph compatibility via a static wrapper that hides dynamic dispatch.

## The Key Experiment

- **ITL reduction vs triton:** 29-69% inter-token latency reduction vs compiler backends on LLM serving benchmarks
- **long context latency:** 28-30% latency reduction for long-context inference
- **parallel generation speedup:** 13-17% speedup for LLM serving with parallel generation

**Compared against:** Triton attention backend; FlashAttention-2; vLLM paged attention; SGLang radix cache attention

**Hardware:** NVIDIA GPU (A100, H100) · **Workloads:** llm-inference; long-context-inference; parallel-generation; prefix-caching

## Why This Approach

BSR as a single unifying KV-cache abstraction that collapses paged, ragged, and tree-structured layouts into one kernel path; CUDAGraph-compatible dynamic load balancing via a static-size priority queue indirection layer.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: Block-sparse row format unifying heterogeneous KV-cache layouts for attention computation.

## What It Leaves Open

- JIT compilation adds first-request latency; warm-up required for production deployment
- BSR block size must be tuned per hardware; sub-optimal block sizes degrade performance
- Load-balanced scheduling overhead may dominate for very short sequences
- Composable format merging requires storing intermediate partial softmax states, increasing SRAM pressure

**Tags:** attention, KV-cache, BSR, JIT, CUDAGraph, LLM-serving, FlashInfer, load-balancing
