# Basilisk: A 34mm² End-to-End Open-Source 64-bit Linux-Capable RISC-V SoC in 130nm BiCMOS

**Venue:** HOTCHIPS
**Authors:** Philippe Sauter, Thomas Benz, Paul Scheffler, Martin Poviser, Frank K. Gürkaynak, Luca Benini
**ID:** hotchips-2025-028
**Confidence:** high

## Problem
End-to-end open-source EDA flows have not demonstrated large, production-grade SoCs; existing approaches scale only to small designs, limiting adoption and supply-chain independence.

## Motivation
Open-source chip design enables supply-chain diversification, zero-trust verification, and collaborative development, critical for security and resilience in semiconductor supply.

## Method
Basilisk uses open-source EDA (Yosys synthesis, OpenROAD place-and-route) to design a 34mm² Linux-capable RISC-V SoC in 130nm BiCMOS. The team enhanced the EDA flow: 2.3x timing improvement and 1.6x area reduction in synthesis, 12% die-size reduction in P&R through technology-aware tuning. The design includes a 64-bit core, 124MB/s DRAM controller, USB 1.1, video output, and 62Mb/s chip-to-chip link.

## Key Novelty
Largest end-to-end open-source SoC to date, proving scalability of open EDA to complex, Linux-capable systems.

## Contributions
- Enhanced Yosys-based synthesis flow improving timing 2.3x and area 1.6x
- Optimized OpenROAD place-and-route reducing die size 12%
- Complete open-source Linux-capable RISC-V SoC in 130nm
- Validated design achieving 62MHz nominal (102MHz at higher voltage), 18.9DPMFLOP/s/W peak efficiency

## Hardware Target
- SoC
- RISC-V

## Technique Categories
- compiler
- circuit-design

## Workloads
(None specified)

## Metrics
- **area:** 34mm²
- **frequency:** 62MHz nominal, 102MHz boosted
- **efficiency:** 18.9DPMFLOP/s/W at 0.88V
- **synthesis_improvement:** 2.3x timing, 1.6x area
- **pr_improvement:** 12% die-size reduction

## Baselines
- Previous open-source designs (smaller scale)
- Commercial EDA flows

## Limitations
Design focuses on correctness and EDA flow; performance not optimized vs modern commercial SoCs.

## Tags
open-source, risc-v, eda, linux-capable, 130nm

## Primary Theme
Large-scale open-source RISC-V SoC via optimized EDA
