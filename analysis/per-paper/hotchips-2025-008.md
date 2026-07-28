# Cuzco: A High-Performance RISC-V RVA23 Compatible CPU IP

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
RISC-V ecosystem lacks high-performance, production-grade CPU implementations; Cuzco provides a high-performance RISC-V core compatible with RVA23 profile for data center and edge deployment.

## Motivation
Open ISA adoption in data centers requires mature CPU designs that match or exceed x86/ARM performance; RISC-V RVA23 specifies a production-grade profile for 64-bit computing workloads.

## Method
Cuzco implements a high-performance RISC-V core with multi-stage pipelined execution, out-of-order instruction scheduling, and caches optimized for latency-sensitive workloads, full compliance with RVA23 ISA specification.

## Key Novelty
Production-grade high-performance RISC-V core implementing full RVA23 profile with performance comparable to contemporary x86/ARM CPUs.

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
