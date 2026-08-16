# PEZY-SC4s: The Fourth Generation MIMD Many-core Processor with High Energy Efficiency and Flexibility for HPC and AI Applications

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
HPC and AI workloads require massive parallelism with energy efficiency; PEZY-SC4s is a fourth-generation many-core processor targeting both traditional HPC and emerging AI inference/training workloads.

## Motivation
Scaling compute to exascale requires energy-efficient processors balancing flexible compute with specialized throughput; many-core architectures provide high FLOPS/watt and software flexibility vs. specialized accelerators.

## Method
The PEZY-SC4s packs hundreds of identical processing cores that can each run different instructions on different data simultaneously (MIMD). Each core connects to a high-speed memory system that can move data in and out quickly, and they use cache coherence (a system to keep shared data consistent when multiple cores access the same data). The connections between cores are flexible, allowing the same hardware to run either traditional scientific computing algorithms or AI workloads.

## Key Novelty
A many-core MIMD processor (where each core runs different instructions on different data) that balances flexibility and energy efficiency to handle both scientific computing and AI workloads.

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
