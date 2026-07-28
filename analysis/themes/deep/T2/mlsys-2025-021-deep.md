# MiLo: Efficient Quantized MoE Inference with Mixture of Low-Rank Compensators

**Venue:** MLSYS 2025 · **Theme:** MoE Low-Rank Quantization

## What It Does

MoE LLMs suffer large accuracy degradation at INT3 weight quantization; existing calibration-free methods yield poor accuracy and existing INT3 kernels lack measured throughput gains at batch size > 1.

MoE models like Mixtral-8x7B are memory-bandwidth-bound at inference; INT3 quantization can dramatically reduce memory footprint but previous approaches (GPTQ, RTN) require calibration data or fail to deliver real speedups at practical batch sizes.

Calibration-free HQQ-based INT3 quantization combined with a mixture of adaptive low-rank compensators (SVD-based residual reconstruction). Compensator rank is selected per-layer based on: (1) dense vs sparse layer type, (2) weight kurtosis, (3) expert activation frequency. Iterative joint optimization of quantized weights and compensators. Both weights and compensators are INT3-packed. Custom W3A16 Tensor Core GeMM kernel with zero-bit-waste INT3 packing, binary manipulation I2F dequantization, async global weight loading, and support for batch size > 1.

## The Key Experiment

- **speedup:** 1.2x over MARLIN backend for Mixtral-8x7B; 3x faster quantization vs GPTQ
- **energy or tops w:** None
- **area:** None
- **ppa:** None
- **accuracy:** Recovers 87%+ accuracy at 22% compression ratio; MiLo-s2 surpasses GPTQ by 17% on Wikitext2 PPL
- **other:** None

**Compared against:** RTN; GPTQ; HQQ; MARLIN backend

**Hardware:** GPU · **Workloads:** LLM-inference; MoE

## Why This Approach

First W3A16 Tensor Core kernel with demonstrated throughput speedup at batch size > 1 for MoE models, combined with calibration-free adaptive low-rank compensation that recovers accuracy without calibration data.

This paper sits in the **quantization** subtheme. The core tension: lower precision = smaller model = less memory bandwidth, but at the cost of rounding error that compounds across layers. This paper's bet: Calibration-free INT3 quantization + mixture of adaptive low-rank compensators (MiLo).

## What It Leaves Open

- Low-rank compensators add inference memory overhead (though also quantized)
- Kernel optimized for NVIDIA A100 Tensor Core ISA; portability not demonstrated
- Expert activation frequency requires profiling runs

**Tags:** MoE, INT3, quantization, low-rank, tensor-core, LLM-inference, Mixtral
