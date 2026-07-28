# CORSAIR: An In-Memory Computing Chiplet Architecture for Inference-Time Compute Acceleration

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
AI inference workloads suffer from high memory bandwidth requirements and latency during matrix operations; CORSAIR proposes a chiplet-based in-memory computing architecture to bring computation closer to data storage.

## Motivation
Inference acceleration requires massive parallelism and data movement; in-memory computing eliminates the von Neumann bottleneck between memory and compute, critical as model sizes grow.

## Method
CORSAIR uses a modular chiplet architecture where each chiplet integrates analog or mixed-signal in-memory computing fabric with local memory, enabling matrix operations directly in the memory substrate while maintaining chiplet-level flexibility through standard interconnects.

## Key Novelty
Chiplet-based decomposition of in-memory computing fabric, allowing scalability through chiplet replication and heterogeneous IMC compute units per chiplet.

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
