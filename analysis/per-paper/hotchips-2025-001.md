# CORSAIR: An In-Memory Computing Chiplet Architecture for Inference-Time Compute Acceleration

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
AI inference workloads suffer from high memory bandwidth requirements and latency during matrix operations; CORSAIR proposes a chiplet-based in-memory computing architecture to bring computation closer to data storage.

## Motivation
Inference acceleration requires massive parallelism and data movement; in-memory computing eliminates the von Neumann bottleneck between memory and compute, critical as model sizes grow.

## Method
CORSAIR builds AI accelerators from modular chiplets—specialized chips where computation circuits sit inside local memory, eliminating slow data transfers between separate memory and processor. Each chiplet contains analog or mixed-signal circuits (electronics using continuous signals rather than pure digital 0s and 1s) that perform matrix operations directly in the memory. Standard interfaces connect chiplets together, allowing flexible scaling by replicating chiplets or combining different compute types within each one.

## Key Novelty
CORSAIR decomposes in-memory computing into modular chiplets—building blocks that can be replicated for scale and mixed with different compute types.

## Contributions
- Chiplet architecture enabling scalable in-memory computing for inference
- Integration of analog IMC fabric within chiplet boundaries
- Standard interconnect enabling multi-chiplet scaling
- Demonstrated inference acceleration on transformer and CNN workloads

## Hardware Targets
ASIC, CIM, chiplet

## Techniques
near-data-processing, parallelism, packaging

## Workloads
LLM-inference, CNN, transformer

## Metrics
- Speedup: varies by workload and precision
- Energy: improved power efficiency vs. GPU inference

## Baselines
GPU inference, CPU inference

## Limitations
Not discussed.

## Tags
imc, chiplet, inference, ai-acceleration, near-data, scalable
