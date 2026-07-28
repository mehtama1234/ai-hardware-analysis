# MEGA.mini: A NPU with Novel Heterogeneous AI Processing Architecture Balancing Efficiency, Performance, and Intelligence for the Era of Generative AI

**Venue:** HOTCHIPS  
**Confidence:** high (abstract provided)

## Problem
AI accelerators must balance low-precision compute efficiency against accuracy preservation for outlier values; MEGA.mini proposes a heterogeneous NPU architecture supporting both fixed-point and floating-point computation dynamically.

## Motivation
Generative AI requires both massive compute efficiency (>95% quantized operations) and numerical precision for activation outliers; hybrid precision enables accuracy without sacrificing efficiency.

## Method
MEGA.mini combines a large fixed-point compute fabric (FXP, >95% operations) with a smaller floating-point unit handling outlier values (<5%), using a big.LITTLE heterogeneous core design that switches between execution modes based on data characteristics. Three hierarchical solutions (MEGA, median, mini) scale across deployment targets.

## Key Novelty
Heterogeneous big.LITTLE architecture intelligently routing quantized vs. outlier data to specialized compute units, enabling adaptive precision with high efficiency.

## Contributions
- Heterogeneous NPU architecture with integrated FXP + FP compute
- Adaptive precision routing based on data outlier detection
- Three hierarchical NPU variants (MEGA/median/mini) for scalable deployment
- >95% efficiency through low-precision fixed-point primary compute

## Hardware Targets
NPU, ASIC

## Techniques
quantization, parallelism, circuit-design

## Workloads
LLM-inference, transformer, diffusion

## Metrics
- Energy: high efficiency through FXP, preserved accuracy via hybrid precision
- Accuracy: >95% computation in low-precision; FP for <5% outliers

## Baselines
Pure quantized NPUs, Full-precision AI accelerators, contemporary mobile NPUs

## Limitations
Scalability to very large models and training phase support not discussed.

## Tags
npu, hybrid-precision, quantization, big-little, generative-ai, adaptive
