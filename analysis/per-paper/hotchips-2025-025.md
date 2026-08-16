# Bit-Separable Transformer Accelerator Leveraging Output Activation Sparsity for Efficient DRAM Access

**Venue:** HOTCHIPS
**Authors:** Seunghyun Park, Daejin Park
**ID:** hotchips-2025-025
**Confidence:** low

## Problem
Transformer inference is memory-bound; DRAM bandwidth limits throughput, especially for attention operations where memory access patterns are irregular.

## Motivation
Activation sparsity in transformers is high but often unexploited in hardware; leveraging sparsity can reduce DRAM bandwidth requirements and improve inference efficiency.

## Method
When neural networks run inference (make predictions), many of the intermediate values they produce are zero or less important—this is called sparse activations. The accelerator stores these values using bit-separable encoding, which breaks numbers down to their individual bits so that zeros and small values take minimal space instead of full memory slots. It combines this with specialized memory access patterns designed to efficiently read and write these compressed values, which reduces the total amount of data traveling between the processor and main memory.

## Key Novelty
Using bit-separable encoding (breaking numbers into individual bits) for sparse activation values reduces the memory bandwidth that transformer inference requires.

## Contributions
- Bit-separable encoding of sparse activations
- Optimized DRAM access patterns for sparsity
- Efficient transformer dataflow exploiting activation sparsity
- Reduced memory bandwidth and latency

## Hardware Target
- ASIC
- FPGA

## Technique Categories
- sparsity
- memory-system
- dataflow

## Workloads
- transformer
- LLM-inference

## Metrics
- **bandwidth:** DRAM GB/s
- **speedup:** vs dense

## Baselines
- Dense transformer accelerators

## Limitations
Specific sparsity assumptions and performance comparisons not detailed.

## Tags
transformer, sparsity, memory, acceleration, dram

## Primary Theme
Sparse-activation-aware transformer accelerator
