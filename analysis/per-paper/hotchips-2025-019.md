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
The system uses three techniques. First, it redesigns memory organization and uses high-bandwidth memory (HBM) with vertically stacked chips (3D stacking) to dramatically increase how much data can flow between memory and processors per second. Second, it creates faster communication pathways between memory and compute units by redesigning the wiring and protocols that connect them. Third, it designs memory and processors as one integrated system rather than independent components, so they can optimize for each other's needs.

## Key Novelty
Instead of focusing on making processors faster, the work identifies memory bandwidth as what actually limits data center performance, and redesigns the entire system around fixing that bottleneck.

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
