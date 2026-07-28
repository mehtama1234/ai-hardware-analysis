# A TRRIP Down Memory Lane: Temperature-Based Re-Reference Interval Prediction For Instruction Caching

**Venue:** MICRO · **Theme:** Thermal-Aware DRAM

## What It Does

Modern mobile CPU workloads (interpreters, JIT compilers, UI frameworks) have large instruction footprints with long reuse distances that defeat hardware-only cache replacement policies, causing persistent L2 instruction cache miss stalls even after PGO code layout optimization.

Mobile code complexity and footprint grow faster than on-chip cache capacity; hardware-centric predictors see only short execution windows and cannot track the global temperature of code sections, leaving significant frontend stalls unaddressed.

TRRIP is a compiler-OS-hardware co-design cache replacement policy. The LLVM PGO compiler classifies basic blocks as hot/warm/cold by execution frequency and places them in separate ELF sections (.text.hot, .text.warm, .text.cold). The OS loader reads these ELF headers and encodes temperature (2 bits) into existing ARM PBHA bits in page table entries (PTEs), requiring no ISA changes. The MMU transfers temperature bits with every memory request to the L2 cache. The hardware replacement policy extends RRIP: hot instruction lines are inserted at Immediate re-reference priority (RRPV=0), warm lines at Near (RRPV=1), cold/data lines at Intermediate (RRPV=2) per the existing RRIP eviction scan. The variant TRRIP-2 additionally decelerates RRPV promotion for non-hot hits. No additional on-chip storage is required beyond existing PTE bits.

## The Key Experiment

- **speedup:** 3.9% geomean over SRRIP baseline (PGO-compiled mobile benchmarks)
- **other:** L2 instruction MPKI reduction of 26.5% (TRRIP-1) and 27.3% (TRRIP-2)

**Compared against:** SRRIP; BRRIP; DRRIP; SHiP; CLIP; Emissary; LRU

**Hardware:** CPU; SoC · **Workloads:** vision; speech

## Why This Approach

Using existing ARM PBHA page-table bits as a zero-storage-overhead channel to pass compiler-derived hot/cold temperature to the L2 cache replacement policy without ISA modifications.

This paper sits in the **memory hierarchy** subtheme. The core constraint: compute starves waiting for data — arithmetic throughput far outpaces DRAM bandwidth. This paper's solution: Characterization of instruction cache miss patterns in PGO-optimized mobile system software showing persistent frontend stalls due to high hot-code reuse distance.

## What It Leaves Open

- Evaluated only on a simulated mobile SoC using proxy benchmarks
- real silicon results and interaction with proprietary system software are not shown.

**Tags:** instruction-cache, cache-replacement, rrip, compiler-hw-codesign, mobile-cpu
