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
The accelerator uses bit-separable representation for sparse activations, compressing output activations to reduce DRAM traffic. It combines this with specialized access patterns optimizing for sparse memory reads/writes.

## Key Novelty
Bit-separable sparse activation encoding reducing DRAM bandwidth for transformer inference.

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
