# AMD RDNA 4 Radeon 9000 Series GPU

**Venue:** HOTCHIPS
**Authors:** Andy Pomianowski, Laks Pappu
**ID:** hotchips-2025-026
**Confidence:** low

## Problem
Consumer and professional GPU workloads demand higher compute throughput and power efficiency; incremental improvements on existing architectures provide limited gains.

## Motivation
GPU architecture iteration enables better performance/watt, improved cache efficiency, and support for emerging workloads (AI, rendering, simulation).

## Method
RDNA 4 builds on RDNA 3 by redesigning three core parts: the compute units (the processor cores that do math), the cache hierarchy (fast memory layers holding frequently-accessed data), and the memory subsystem (how data travels between the processor and main memory). These improvements increase the GPU's computational output per watt of power, making it work well for both gaming and professional compute tasks like AI training.

## Key Novelty
RDNA 4 achieves higher performance and efficiency per watt by redesigning its compute units and memory architecture to serve both consumer gaming and professional computing workloads.

## Contributions
- Increased compute unit density and efficiency
- Improved cache hierarchy and memory bandwidth
- Enhanced support for compute workloads (AI, simulation)
- Power efficiency gains vs RDNA 3

## Hardware Target
- GPU

## Technique Categories
- circuit-design
- cache
- memory-system

## Workloads
- vision
- LLM-inference

## Metrics
- **compute:** TFLOPS
- **power:** TDP
- **cache:** GB

## Baselines
- RDNA 3
- NVIDIA RTX 40-series

## Limitations
Specific architectural improvements and performance numbers not in title.

## Tags
gpu, rdna, amd, gaming, compute

## Primary Theme
Next-generation consumer/professional GPU
