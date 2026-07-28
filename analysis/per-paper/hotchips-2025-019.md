# Memory: Almost The Only Thing That Matters : A revolution in memory architecture for the data center

**Venue:** HOTCHIPS
**Authors:** Mark Kuemerle
**ID:** hotchips-2025-019
**Confidence:** low

## Problem
Data center performance bottleneck has shifted from computation to memory bandwidth and latency; traditional DRAM hierarchies and interconnects cannot keep pace with compute acceleration.

## Motivation
AI workloads (especially LLMs) are fundamentally memory-bound; improving memory subsystem throughput directly improves end-to-end system performance.

## Method
The work proposes architectural innovations in memory hierarchy, bandwidth, and interconnect design. Likely includes advanced memory technologies (HBM, 3D stacking), new interconnect protocols, and memory-compute co-design.

## Key Novelty
Reframing data center architecture around memory as the primary performance lever, with compute secondary.

## Contributions
- Memory bandwidth architecture innovations for AI workloads
- Novel memory hierarchy design
- Interconnect upgrades to support memory-compute co-optimization
- Data center memory scaling strategies

## Hardware Target
- GPU
- ASIC
- SoC

## Technique Categories
- memory-system
- interconnect

## Workloads
- LLM-inference
- LLM-training

## Metrics
- **bandwidth:** data center throughput
- **latency:** memory access

## Baselines
- Traditional DRAM hierarchies
- Conventional GPUs

## Limitations
Specific technical mechanisms and performance numbers not in title alone.

## Tags
memory, bandwidth, datacenter, ai, architecture

## Primary Theme
Memory-centric data center architecture for AI
