# Adelia: A 4nm LLM Processor for Efficient Generative AI Inference

**Venue:** HOTCHIPS
**Authors:** Seungjae Moon, Jung-Hoon Kim, Juntaek Oh, Jay Kim, Joo-Young Kim
**ID:** hotchips-2025-024
**Confidence:** low

## Problem
LLM inference at scale requires efficient hardware; GPUs consume significant power and memory for attention mechanisms, creating bottlenecks for on-device and cloud inference.

## Motivation
Specialized LLM inference accelerators reduce power, memory, and cost compared to general-purpose GPUs, improving deployability in edge and data center.

## Method
Adelia is a custom ASIC in 4nm process with specialized dataflow for LLM operations (matrix-multiply, attention, FFN). It includes optimized memory hierarchy (on-chip SRAM + external HBM), quantization support (mixed-precision), and attention-specific kernels.

## Key Novelty
4nm LLM inference ASIC optimizing for both throughput and energy efficiency through attention-aware hardware design.

## Contributions
- Custom hardware dataflow for transformer-efficient LLM inference
- 4nm process enabling low power and high density
- Support for various model sizes and quantization schemes
- Demonstrated efficiency vs GPU baselines

## Hardware Target
- ASIC

## Technique Categories
- circuit-design
- dataflow
- memory-system

## Workloads
- LLM-inference
- transformer

## Metrics
- **power:** W
- **throughput:** tokens/sec
- **area:** mm²

## Baselines
- NVIDIA GPUs
- TPUs
- Other LLM ASICs

## Limitations
Specific performance metrics and detailed architectural comparison not in title.

## Tags
llm, asic, inference, 4nm, efficient

## Primary Theme
4nm ASIC for efficient LLM inference
