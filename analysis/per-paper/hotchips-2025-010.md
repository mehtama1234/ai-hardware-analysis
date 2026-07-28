# PEZY-SC4s: The Fourth Generation MIMD Many-core Processor with High Energy Efficiency and Flexibility for HPC and AI Applications

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
HPC and AI workloads require massive parallelism with energy efficiency; PEZY-SC4s is a fourth-generation many-core processor targeting both traditional HPC and emerging AI inference/training workloads.

## Motivation
Scaling compute to exascale requires energy-efficient processors balancing flexible compute with specialized throughput; many-core architectures provide high FLOPS/watt and software flexibility vs. specialized accelerators.

## Method
PEZY-SC4s integrates hundreds of identical cores in an MIMD (multiple-instruction multiple-data) architecture with high memory bandwidth, cache coherence, and flexible interconnect enabling both traditional HPC algorithms and AI workloads.

## Key Novelty
Fourth-generation MIMD many-core processor balancing flexibility and energy efficiency for both HPC and generative AI workloads.

## Contributions
- Fourth-generation many-core processor with improved core count and cache
- Energy-efficient MIMD architecture supporting flexible workloads
- High memory bandwidth for both HPC and AI applications
- Demonstrated scalability on HPC benchmarks and AI inference

## Hardware Targets
CPU, ASIC

## Techniques
parallelism, circuit-design, memory-system

## Workloads
HPC, LLM-inference, transformer

## Metrics
- Performance: improved performance per generation
- Energy: high FLOPS/watt efficiency

## Baselines
PEZY-SC3, GPU accelerators, traditional HPC CPUs

## Limitations
Not discussed.

## Tags
many-core, hpc, ai-inference, mimd, energy-efficient, flexibility
