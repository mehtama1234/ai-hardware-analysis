# Presto: A Unified RISC-V-Compatible SoC for Multi-Scheme FHE Acceleration over Module Lattice

**Venue:** HOTCHIPS
**Authors:** Luchang Lei, Yu Duan, Cheng Peng, Yongqing Zhu, Gangfeng Du, Zhenyu Guan, Huazhong Yang, Yongpan Liu
**ID:** hotchips-2025-020
**Confidence:** low

## Problem
Fully homomorphic encryption (FHE) enables computation on encrypted data but incurs orders of magnitude computational overhead; software FHE is impractical for latency-sensitive applications.

## Motivation
Privacy-preserving cloud computation and secure multi-party computation require efficient FHE, driving need for specialized hardware.

## Method
Presto integrates a RISC-V core with specialized hardware accelerators for polynomial operations (NTT, convolution) and module lattice arithmetic. It supports multiple FHE schemes (BGV, CKKS) through flexible dataflow and instruction extensions.

## Key Novelty
Multi-scheme FHE SoC combining RISC-V control with lattice-optimized accelerators for practical encrypted computation.

## Contributions
- Hardware acceleration for NTT and polynomial multiplication in FHE
- RISC-V-compatible SoC architecture supporting multiple FHE schemes
- Module lattice optimization reducing latency
- Seamless integration of FHE workloads with general-purpose compute

## Hardware Target
- SoC
- ASIC
- RISC-V

## Technique Categories
- circuit-design
- dataflow

## Workloads
- cryptography

## Metrics
- **throughput:** FHE operations/sec
- **latency:** encryption operations

## Baselines
- CPU-based FHE
- Previous FHE accelerators

## Limitations
Specific performance numbers (speedup vs software) and detailed comparison with other accelerators not provided.

## Tags
fhe, cryptography, lattice, risc-v, security

## Primary Theme
RISC-V SoC for accelerated multi-scheme FHE
