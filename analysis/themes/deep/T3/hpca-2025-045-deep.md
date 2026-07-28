# Multi-Dimensional Vector ISA Extension for Mobile In-Cache Computing

**Venue:** HPCA · **Theme:** In-Cache Vector Processing

## What It Does

Existing long-vector ISA extensions (RISC-V RVV, Arm SVE) provide only 1D strided and random memory accesses, which cannot efficiently utilize the 8192-lane SIMD width of in-SRAM vector engines built from mobile L2 caches because mobile data-parallel kernels expose limited 1D parallelism (average 635 elements) across multiple multi-dimensional data structures.

In-cache computing repurposes SRAM cache arrays into wide vector engines at low area cost, but without multi-dimensional memory access instructions the instruction issue bottleneck and low lane utilization (23% for bit-serial with RVV) prevent realizing their throughput advantage over conventional 128-bit mobile SIMD units.

MVE (Multi-dimensional Vector ISA Extension) introduces up to 4D strided and random vector memory accesses, where each dimension can use stride modes: replicate (stride=0), sequential (stride=1), row-stride (stride=previous_dim x length), or arbitrary CR-configured stride. A dimension-level masked execution mechanism masks entire outer-dimension iterations using a compact mask control register, avoiding expensive per-lane scalar mask computation. The ISA operates on physical registers spanning all in-SRAM compute arrays (8192 lanes of 32-bit data), with a cache-geometry-hiding register abstraction. The MVE controller in the L2 cache flattens multi-dimensional logical register accesses to physical SRAM bitline coordinates, uses a Transpose Memory Unit (TMU) with 8T transpose bit-cells and a crossbar to route data into vertical bit-serial layout, and manages cache coherency by checking L1 presence bits and evicting L1 lines before in-cache writes. Compiler support includes liveness analysis for register width, list-hybrid instruction scheduling, and greedy register allocation to minimize in-cache register spills.

## The Key Experiment

- **speedup:** 2.9x vs Arm Neon; 9.3x vs Adreno 640 GPU; 2.0x vs RISC-V RVV on same in-cache engine; 1.5x vs Duality Cache (SIMT model)
- **energy or tops w:** 8.8x energy reduction vs Arm Neon; 5.2x energy reduction vs Adreno 640 GPU
- **area:** 3.6% area overhead to mobile core (at 7nm)

**Compared against:** Arm Neon (Cortex-A76 128-bit ASIMD); Qualcomm Adreno 640 GPU; RISC-V RVV on same in-cache bit-serial engine; Duality Cache (SIMT in-cache model); VRAM (bit-parallel); EVE (bit-hybrid); CAPE (associative computing)

**Hardware:** CPU; CIM (compute-in-memory); SoC · **Workloads:** CNN; vision; speech

## Why This Approach

A multi-dimensional vector ISA (up to 4D strided + random memory accesses with dimension-level masked execution) that hides cache geometry from programmers while raising in-cache SIMD lane utilization from 23% to 60% for mobile workloads.

This paper sits in the **memory hierarchy** subtheme. The core constraint: compute starves waiting for data — arithmetic throughput far outpaces DRAM bandwidth. This paper's solution: MVE ISA with 4D strided and random memory accesses plus dimension-level masked execution, improving bit-serial in-cache utilization from 23% to 60% and performance by 3.8x over RISC-V RVV on the same engine.

## What It Leaves Open

- MVE requires flushing dirty L2 cache lines to switch between cache and compute modes (taking under 2% of execution time in benchmarks), and performance degrades for workloads with large scalar instruction fractions (e.g., zlib reduction kernel achieves only 37% improvement).

**Tags:** in-cache-computing, isa-extension, mobile-processor, sram-compute, multi-dimensional-vector, in-sram
