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
Adelia is a purpose-built computer chip (an ASIC) made at 4nm—an extremely small manufacturing scale that makes transistors energy-efficient—specifically for running large language models. The chip includes separate optimized hardware for the three core LLM operations: matrix multiplication (fast math on grids of numbers), attention (the mechanism that determines which parts of the input are most relevant), and feed-forward networks (layered mathematical transformations). To manage data efficiently, it uses a two-tier memory system: fast, small on-chip SRAM for active processing and larger external HBM (high-bandwidth memory) for bulk storage. It also supports mixed-precision quantization—storing some numbers with fewer bits than others—to reduce power and memory usage without significantly harming accuracy.

## Key Novelty
Adelia achieves fast, power-efficient LLM inference by designing a 4nm chip with a hardware architecture built specifically for attention mechanisms—the operation that selects which input parts matter most.

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
