# MCBP: A Memory-Compute Efficient LLM Inference Accelerator Leveraging Bit-Slice-enabled Sparsity and Repetitiveness

**Venue:** MICRO · **Theme:** Hardware-Fused Attention

## What It Does

LLM inference faces three simultaneous bottlenecks—GEMM computation in the prefill stage, weight loading during decoding (52.4% of short-prompt latency for LLaMA-7B), and KV cache loading for long contexts—which existing Transformer accelerators address in isolation at value granularity, missing fine-grained bit-level optimization opportunities.

Decoder-only LLMs in autoregressive decoding are severely memory-bound, yet quantized weights exhibit bit-slice-level sparsity up to 10x higher than value-level sparsity and bit-slice-level column repetitiveness that enables up to 5.1x computation reduction—properties that are invisible to value-level accelerators.

MCBP is an algorithm-hardware co-design operating at bit-slice (BS) granularity. Three key techniques: (1) BS-Repetitiveness-enabled Computation Reduction (BRCR): decomposes a k-bit weight matrix into k BS matrices, groups m rows into a Group matrix, identifies repeated column vectors via a Content Addressable Memory (CAM) unit, computes a Merged Activation Vector (MAV) for repeated activations (H*(1-bs) additions), and reconstructs output via an Enumeration matrix (m*2^(m-1) additions), achieving up to 12.1x computation reduction vs. value-sparsity. (2) BS-Sparsity-enabled Two-State Coding (BSTC): stores weights in sign-magnitude format; high-order bit-slice matrices (bits 3-7 in INT8) exhibit >65% sparsity and are encoded with two states ({0} for zeros, {1,m-bit data} for non-zeros) at the same group granularity m as BRCR, achieving positive compression without requiring bit reordering for computation; low-order bits (1,2,8) remain uncompressed. (3) Bit-grained Progressive Prediction (BGPP): estimates attention scores MSB-to-LSB across multiple rounds; a radius-scaled filter (threshold = max(A_hat) - alpha * radius) eliminates Keys whose partial score falls below the threshold after each round, enabling early termination that reduces KV cache accesses by up to 50%. Hardware: CAM-based BRCR unit, lightweight parallel BSTC encoder/decoder, clock-gated BGPP prediction module, on-chip SRAM hierarchy (384KB token, 768KB weight, 96KB temp), and external HBM.

## The Key Experiment

- **speedup:** 9.43x vs. NVIDIA A100 GPU
- **energy or tops w:** 22740 GOPS/W average energy efficiency; 31.1x vs. A100 GPU; 35x vs. Spatten; 5.2x vs. FACT; 3.2x vs. SOFA
- **area:** None
- **ppa:** None
- **accuracy:** None
- **other:** BGPP reduces KV cache accesses by up to 50%; BRCR achieves 5.1x group-wise computation reduction vs. full-size merge across 5 LLMs

**Compared against:** NVIDIA A100 GPU (with TensorRT-LLM); Spatten; FACT; SOFA; Sanger; SpAtten; A3; ELSA; DTATrans

**Hardware:** ASIC; GPU · **Workloads:** LLM-inference; attention; transformer

## Why This Approach

A unified bit-slice-granularity co-design that simultaneously exploits bit-level repetitiveness (via CAM-based grouped matching), bit-level sparsity in high-order weight planes (via two-state coding), and progressive bit-by-bit KV cache filtering (BGPP) to jointly address all three LLM inference bottlenecks at a finer granularity than any prior accelerator.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: BRCR: bit-slice repetitiveness-based GEMM computation reduction using CAM-based grouped column matching, achieving up to 12.1x computation reduction vs. value-sparsity and 3.8x vs. naive bit-serial.

## What It Leaves Open

- MCBP requires offline BSTC weight pre-compression, adding pre-deployment overhead
- the BGPP progressive prediction introduces multi-round latency that must be overlapped with BRCR computation
- optimal group size m is model-dependent and requires design-space exploration.

**Tags:** llm-inference, bit-serial, sparsity, quantization, transformer-accelerator, kv-cache
