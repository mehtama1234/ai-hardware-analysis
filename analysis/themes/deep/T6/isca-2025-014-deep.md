# HPVM-HDC: A Heterogeneous Programming System for Accelerating Hyperdimensional Computing

**Venue:** ISCA · **Subtheme:** Parallel Programming Abstractions

## What It Does

The system provides two components: HDC++, a C++-based DSL built on Hetero-C++ that exposes 24 HDC-specific primitives (hypervector/hypermatrix ops, Hamming distance, cosine similarity, encoding/training/inference loop constructs) in a target-agnostic unified programming model; and HPVM-HDC, a heterogeneous compiler that extends LLVM/HPVM IR with HDC-specific intrinsics and compiles HDC++ to CPUs (via HPVM CPU backend), GPUs (via CUDA/cuBLAS/Thrust), a 40nm digital HDC ASIC (Hamming-distance pipelined, 0.78 TOPS/W), and a ReRAM HDC accelerator simulator. Two approximation optimizations exploit HDC error resilience: automatic binarization propagation (taint analysis reducing element bitwidth to 1 bit) and reduction perforation (strided or segmented loop iteration over hypervector dimensions for Hamming/cosine similarity and matmul operations).

HDC++'s high-level stage primitives (encoding_loop, training_loop, inference_loop) allow the same source to be lowered to coarse-grained accelerator instructions on ASICs/ReRAM and to fine-grained CUDA/HPVM IR on CPUs/GPUs, enabling the first execution of complete HDC applications on both a taped-out digital ASIC and a ReRAM accelerator.

## The Key Result

- **Speedup:** 1.17x geomean over optimized CUDA on GPU; up to 3.4x with approximation optimizations
- **Other:** 1.6x reduction in total LOC across CPU+GPU baselines; first HDC application execution on digital ASIC and ReRAM accelerator

## Why This Approach

HDC++: first HDC-specific high-level programming language with 24 target-agnostic primitives including coarse-grain stage-level constructs for accelerator targeting. HPVM-HDC: first retargetable compiler for HDC generating code for CPUs, GPUs, a digital ASIC (40nm), and a ReRAM accelerator simulator from a single source. Automatic binarization and reduction perforation compiler optimizations exploiting HDC error resilience, achieving up to 3.4x GPU speedup with marginal accuracy loss. 1.17x geomean GPU speedup over optimized CUDA baselines and 1.6x reduction in total lines of code across 5 HDC applications

This work addresses the fundamental problem: Hyperdimensional Computing (HDC) programs are manually written in target-specific languages (CUDA, C++, Python) that cannot be retargeted to HDC-specific accelerators (digital ASICs, ReRAM devices), a...

## What It Leaves Open

- Approximation optimizations (binarization, reduction perforation) are not automatically selected — the programmer must specify them; automatic selection of optimal approximation configurations is left to future work.
