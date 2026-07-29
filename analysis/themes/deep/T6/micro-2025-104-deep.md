# ReGate: Enabling Power Gating in Neural Processing Units

**Venue:** MICRO · **Subtheme:** Dataflow Compilation

## What It Does

ReGate uses hardware-software co-design differentiated by component. For systolic arrays (SAs): non-zero weight detection generates row/column bitmaps (col_nz, row_nz), and a prefix-sum circuit derives which rows/columns should be powered off; PE-level power gating then follows the diagonal weight-stationary dataflow — the PE_on signal propagates diagonally from the SA input, overlapping wake-up with computation to expose only single-PE wake-up latency. For ICI and HBM controllers: a lightweight hardware-based idle-detection state machine gates these units between collective operators (AllReduce, AllGather). For vector units and SRAM: a new NPU ISA extension adds setpm instructions with three modes (on/auto/off) that let the ML compiler insert power-management instructions at statically-known idle boundaries — the compiler determines VU idle gaps from instruction scheduling and SRAM capacity from tile-size analysis.

Diagonal-dataflow-aware cycle-level PE power gating in systolic arrays, where the PE_on signal propagates through the array following the inherent weight-stationary diagonal dataflow, enabling fine-grained power gating with only single-PE wake-up latency overhead.

## The Key Result

- **Energy Or Tops W:** 8.5%-32.8% energy reduction (15.5% average) vs. no power gating
- **Other:** <0.5% performance degradation; <3.3% area overhead; 31.1%-62.9% carbon emission reduction at fleet scale

## Why This Approach

First quantification of power-gating opportunities across all major NPU components (SA, VU, SRAM, ICI, HBM) using multi-generation TPU-derived simulators. Diagonal-dataflow-aware PE-level power gating for systolic arrays using row/column non-zero weight detection and PE_on signal propagation. NPU ISA extension (setpm instruction) enabling software-managed power gating for vector units and SRAM with on/auto/off modes. 15.5% average (up to 32.8%) energy reduction across LLM training/inference, DLRM, and stable diffusion workloads with <0.5% performance overhead and <3.3% area overhead at 7nm

This work addresses the fundamental problem: Modern NPU chips (e.g., Google TPU generations) waste 30-72% of their active energy on static (leakage) power because they lack fine-grained power management support; conventional CPU/GPU power-gating...

## What It Leaves Open

- The power-gating analysis excludes peripheral components (PCIe, chip management, control logic) that account for ~40% of static energy; evaluation is on a simulator validated against real TPU data rather than fabricated silicon.
