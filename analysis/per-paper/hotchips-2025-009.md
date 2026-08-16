# MEGA.mini: A NPU with Novel Heterogeneous AI Processing Architecture Balancing Efficiency, Performance, and Intelligence for the Era of Generative AI

**Venue:** HOTCHIPS  
**Confidence:** high (abstract provided)

## Problem
AI accelerators must balance low-precision compute efficiency against accuracy preservation for outlier values; MEGA.mini proposes a heterogeneous NPU architecture supporting both fixed-point and floating-point computation dynamically.

## Motivation
Generative AI requires both massive compute efficiency (>95% quantized operations) and numerical precision for activation outliers; hybrid precision enables accuracy without sacrificing efficiency.

## Method
MEGA.mini runs AI computations through two parallel systems: a large fixed-point unit (fast, simple math) that handles over 95% of operations on normal data values, and a smaller floating-point unit (precise math) that handles less than 5% of operations on unusual outlier values. The hardware automatically detects which system should handle each piece of data and routes it accordingly, switching between the two paths based on the numbers it encounters. Three versions (MEGA, median, mini) scale the design down for different deployment targets from data centers to embedded devices.

## Key Novelty
Splitting AI computation between two cores—one fast (fixed-point) for regular data and one precise (floating-point) for unusual values—with automatic selection of which to use.

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
