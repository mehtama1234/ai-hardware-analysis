# VQ-LLM: High-performance Code Generation for Vector Quantization Augmented LLM Inference

**Venue:** HPCA · **Theme:** Vector Quantization for LLMs

## What It Does

Vector quantization (VQ) achieves higher compression ratios than element-wise quantization for LLM weights and KV cache (down to 1-2 bits), but existing VQ kernel implementations are slower than FP16 baselines due to two root causes: inefficient codebook access (excessive shared memory usage, bank conflicts, poor L1 hit rate at 12.45%) and uncoordinated dataflow between codebook loading and subsequent GEMM/attention computation (duplicated off-chip loads and shared-memory-to-register layout mismatches).

LLMs are heavily memory-bound and VQ can compress weights/KV-cache more aggressively than element-wise INT4, but without efficient GPU kernels the memory savings cannot translate to latency improvements, making VQ impractical despite its accuracy advantage.

VQ-LLM introduces a codebook cache abstraction that hierarchically places codebook entries across GPU memory levels based on offline-profiled access frequency: hot entries in thread-local registers (eliminating bank conflicts), medium-frequency entries in shared memory, and cold entries in global memory, with two configurable boundaries. Centered on this cache, the codebook-centric dataflow partitions and parallelizes computation along codebook-switch axes (rather than reduction axes) so each thread block loads exactly one codebook, eliminating duplicate global-to-shared traffic; an adaptive split factor balances the resulting global reduction overhead. Codebook-centric hierarchical fusion extends shared-memory-level fusion with register-level fusion using GPU intra-warp shuffle (shfl.xor) instructions to rearrange dequantized data layouts without shared memory round-trips, with the fusion level chosen adaptively based on the number of shuffle operations required versus shared-memory latency. Adaptive heuristics tune nreg, nshared, and the split factor per VQ configuration and GPU.

## The Key Experiment

- **speedup:** 64.36% to 99.1% latency reduction vs open-source VQ implementations
- **other:** Competitive with AWQ and QoQ at equivalent bit-widths on RTX 4090 and A40
- **energy or tops w:** None
- **area:** None
- **ppa:** None
- **accuracy:** None

**Compared against:** FP16 FlashDecoding baseline; AWQ; QoQ; open-source VQ kernels (AQLM, QuiP#, GPTVQ)

**Hardware:** GPU · **Workloads:** LLM-inference; attention

## Why This Approach

A codebook cache abstraction with frequency-based hierarchical placement (register/shared/global) combined with codebook-centric dataflow partitioning and register-level intra-warp shuffle fusion, converting VQ from a latency liability into a practical speedup over element-wise quantization.

This paper sits in the **quantization** subtheme. The core tension: lower precision = smaller model = less memory bandwidth, but at the cost of rounding error that compounds across layers. This paper's bet: Profiling analysis identifying two root causes of VQ kernel inefficiency: codebook placement causing shared-memory pressure/bank-conflicts, and uncoordinated dataflow causing redundant global-to-shared traffic and layout-mismatch shared-to-register traffic.

## What It Leaves Open

- Codebook frequency profiling is done offline per model/hardware combination
- runtime changes in access patterns (e.g., different batch sizes or sequence lengths) may require re-profiling.

**Tags:** vector-quantization, llm-inference, gpu-kernel, codebook, kernel-fusion, kv-cache
