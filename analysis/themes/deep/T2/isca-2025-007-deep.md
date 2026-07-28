# Oaken: Fast and Efficient LLM Serving with Online-Offline Hybrid KV Cache Quantization

**Venue:** ISCA · **Theme:** Hybrid Online/Offline Quantization

## What It Does

LLM serving with large batch sizes is bottlenecked by KV cache memory bandwidth and capacity: HBM provides high bandwidth but limited capacity, while high-capacity LPDDR memory lacks bandwidth. Existing KV cache quantization approaches either incur excessive online outlier detection overhead (e.g., topK sorting at O(n log n)) or sacrifice accuracy through coarse-grained grouping.

As LLM context lengths and serving batch sizes grow, the KV cache dominates memory usage and becomes the primary throughput bottleneck, making efficient quantization with low runtime overhead essential for cost-effective inference.

Oaken uses an online-offline hybrid KV cache quantization scheme: offline profiling (~100 inferences) determines per-layer, data-agnostic outlier thresholds, which are applied online to partition per-token KV vectors into three groups (outer/large outliers, inner/small outliers, middle/inliers). Group-shift quantization subtracts offline thresholds to narrow each group's value range before applying 4/5-bit uniform quantization. Outliers are stored in COO sparse format fused into zeroed elements of the dense 4-bit inlier matrix (8 bits per sparse entry total), and a custom DMA-integrated quantization/dequantization engine with a page-based MMU handles bandwidth-maximizing burst memory access. The accelerator is built on an LPU architecture synthesized in TSMC 28nm with HBM or LPDDR memory.

## The Key Experiment

- **speedup:** 1.79x over vLLM, 1.58x over QServe at batch size 256
- **accuracy:** 0.54% average accuracy loss vs. state-of-the-art KV quantization baselines
- **area:** 8.21% area overhead for Oaken modules
- **other:** KV bitwidth reduction up to 70%; synthesized at TSMC 28nm

**Compared against:** NVIDIA A100 GPU (vLLM); QServe; KVQuant; KIVI; Tender; Atom; LPU

**Hardware:** ASIC; NPU · **Workloads:** LLM-inference; attention; MoE

## Why This Approach

Offline profiling of per-layer KV distribution thresholds eliminates expensive online sorting while enabling fine-grained mixed-precision grouping, and fused dense-and-sparse encoding reduces outlier storage from 23 to 8 bits per entry.

This paper sits in the **quantization** subtheme. The core tension: lower precision = smaller model = less memory bandwidth, but at the cost of rounding error that compounds across layers. This paper's bet: Online-offline hybrid KV cache quantization that avoids O(n log n) online sorting by using offline-profiled thresholds for three-group value partitioning.

## What It Leaves Open

- Offline profiling must be repeated per model, and the fixed group ratio (4%/90%/6%) may be suboptimal for models with highly atypical KV distributions.

**Tags:** kv-cache, quantization, llm-serving, mixed-precision, memory-bandwidth
