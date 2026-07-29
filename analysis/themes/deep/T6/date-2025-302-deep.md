# Fast Interpreter-Based Instruction Set Simulation for Virtual Prototypes

**Venue:** DATE · **Subtheme:** Hardware Simulation

## What It Does

Proposes Dynamic Basic Block Cache (DBBCache) to accelerate instruction processing and Load/Store Cache (LSCache) to speed up memory operations in interpreter-based RISC-V ISS; implemented on SystemC-based VP.

Combined DBBCache and LSCache optimization achieving high performance while maintaining interpreter comprehensibility and adaptability.

## The Key Result

- **Mips:** 406.97
- **Speedup Vs Original:** 8.98×
- **Speedup Vs Spike:** 1.65×

## Why This Approach

Dynamic Basic Block Cache for instruction processing acceleration. Load/Store Cache for memory operation optimization. Peak performance of 406.97 MIPS. 8.98× speedup over original VP, 1.65× over Spike simulator. RISC-V Zfh half-precision extension support. Open-source release

This work addresses the fundamental problem: Interpreter-based instruction set simulators for virtual prototypes have poor performance; optimizations often sacrifice comprehensibility and adaptability.

## What It Leaves Open

- Not discussed.
