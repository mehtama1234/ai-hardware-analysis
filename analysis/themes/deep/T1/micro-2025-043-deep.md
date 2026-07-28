# Dissecting and Modeling the Architecture of Modern GPU Cores

**Venue:** MICRO · **Theme:** GPU Microarchitecture for Attention

## What It Does

Academic GPU microarchitecture simulators such as Accel-sim rely on pipeline models derived from NVIDIA Tesla (2006), missing 15+ years of GPU core evolution including compiler-guided dependency management, the L0 instruction cache, register file cache, and updated issue logic in Ampere-class SMs. This causes simulation inaccuracy that misleads research conclusions.

GPU microarchitecture research requires accurate simulators; existing models diverge significantly from modern NVIDIA designs, producing flawed performance predictions for HPC and ML workloads.

The authors reverse-engineer the NVIDIA Ampere (RTX A6000) SM pipeline using hand-written SASS microbenchmarks that measure cycle-precise instruction timings. They uncover a software-hardware co-design dependency mechanism using per-warp Stall counters and six Dependence counters (SBx) encoded as ISA control bits replacing traditional scoreboards, a Compiler-Guided Greedy-Then-Youngest (CGGTY) warp issue policy, a two-bank register file without collector units, a compiler-managed 6-entry register file cache (RFC), an L0 instruction cache with a 16-entry stream buffer prefetcher, and detailed memory pipeline queue sizing and latencies. All findings are integrated into a rebuilt Accel-sim model validated against real hardware.

## The Key Experiment

- **accuracy:** 13.98% mean MAPE on NVIDIA RTX A6000 (Ampere); 18.24% MAPE improvement over Accel-sim baseline

**Compared against:** Accel-sim (prior state-of-the-art GPU simulator); GPGPU-Sim

**Hardware:** GPU · **Workloads:** HPC; LLM-inference; LLM-training

## Why This Approach

Complete reverse-engineering of modern NVIDIA Ampere SM pipelines revealing that dependency management is handled entirely via compiler-encoded ISA control bits (Stall/Dependence counters), eliminating hardware scoreboards and collector units.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: Full characterization of the CGGTY warp issue scheduler policy with readiness conditions and yield/stall control bits.

## What It Leaves Open

- Experiments cover only same-CTA warp interactions
- cross-CTA scheduling behavior and multi-SM interactions are not characterized.

**Tags:** gpu-microarchitecture, reverse-engineering, warp-scheduling, register-file, simulation
