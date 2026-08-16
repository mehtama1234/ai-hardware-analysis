# Cuzco: A High-Performance RISC-V RVA23 Compatible CPU IP

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
RISC-V ecosystem lacks high-performance, production-grade CPU implementations; Cuzco provides a high-performance RISC-V core compatible with RVA23 profile for data center and edge deployment.

## Motivation
Open ISA adoption in data centers requires mature CPU designs that match or exceed x86/ARM performance; RISC-V RVA23 specifies a production-grade profile for 64-bit computing workloads.

## Method
Cuzco implements a RISC-V processor using pipelined execution that divides each instruction's work into stages, allowing multiple instructions to progress simultaneously in an overlapping manner. It reorders instructions dynamically whenever safe to do so, keeping the processor busier and working more efficiently. The design includes cache memory tuned to minimize delays for latency-sensitive operations. It achieves full compliance with RVA23, the standardized RISC-V instruction set.

## Key Novelty
Cuzco provides a production-ready, high-performance RISC-V processor implementing the full RVA23 standard, with performance comparable to modern x86 and ARM processors.

## Contributions
- High-performance RISC-V RVA23-compatible CPU IP
- Out-of-order execution with latency-optimized microarchitecture
- Efficient cache hierarchy supporting modern workloads
- Demonstrated performance parity with x86/ARM competitors

## Hardware Targets
CPU, RISC-V

## Techniques
parallelism, circuit-design, cache

## Workloads
HPC, LLM-inference

## Metrics
- Performance: competitive with x86/ARM at similar process node
- Area: optimized core footprint

## Baselines
x86-64 CPUs, ARM Cortex CPUs, other RISC-V cores

## Limitations
Not discussed.

## Tags
risc-v, cpu, high-performance, rva23, open-isa, production
