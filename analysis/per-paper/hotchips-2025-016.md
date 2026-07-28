# A 4.69mW LLM Processor with Binary/Ternary Weights for Billion-Parameter Llama Model

**Venue:** HOTCHIPS
**Authors:** Sangyeob Kim, Jungwan Lee, Byeongju Kim, Hoi-Jun Yoo
**ID:** hotchips-2025-016
**Confidence:** low

## Problem
Running billion-parameter LLMs on edge devices requires extreme power efficiency; standard precision weights consume orders of magnitude more power than practical for mobile/IoT.

## Motivation
On-device LLM inference enables privacy, low-latency response, and reduced cloud costs, but power consumption is the primary bottleneck.

## Method
The processor uses binary and ternary weight quantization (extreme 1-2 bit precision) combined with specialized compute units optimized for low-precision arithmetic. Custom dataflow exploits weight sparsity patterns from quantization, reducing memory bandwidth and computation.

## Key Novelty
Sub-5mW inference of Llama models through extreme quantization (binary/ternary) paired with hardware acceleration for ultra-low-precision matrix operations.

## Contributions
- Hardware design achieving 4.69mW for billion-parameter LLM inference
- Binary/ternary weight quantization methodology maintaining model accuracy
- Specialized compute pipeline for 1-2 bit arithmetic
- Energy-efficient SRAM-based weight storage avoiding DRAM

## Hardware Target
- ASIC
- NPU

## Technique Categories
- quantization
- circuit-design
- power

## Workloads
- LLM-inference

## Metrics
- **power:** 4.69mW
- **area:** estimated <10mm²

## Baselines
- Standard FP32/INT8 LLM inference
- CPU/GPU edge inference

## Limitations
Accuracy impact of extreme quantization and comparison with other edge LLM processors not detailed.

## Tags
llm, quantization, edge, low-power, asic

## Primary Theme
Ultra-low-power LLM inference via extreme quantization
