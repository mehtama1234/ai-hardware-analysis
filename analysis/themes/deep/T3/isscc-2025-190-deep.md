# 2.2 IBM Telum II: Next Generation 5.5GHz Microprocessor with On-Die Data Processing Unit and Improved AI Accelerator

**Venue:** ISSCC · **Theme:** On-Die AI Inference

## What It Does

Enterprise server workloads (z/OS) require high single-thread performance, large on-chip cache capacity, and specialized acceleration for AI and data processing. Previous generations face memory bandwidth bottlenecks for data-intensive workloads and limited AI compute integration.

Enterprise AI adoption demands servers with integrated AI acceleration alongside high-performance general-purpose cores, large shared cache for memory-intensive workloads, and improved system scalability (multi-drawer coherency).

Telum II is a 600mm² die in Samsung 5nm containing 43B transistors and 8 cores per chip (CP) operating at 5.5GHz. Key enhancements: (1) new on-die Data Processing Unit (DPU) for AI and data acceleration, (2) cache expansion: 10 L2 instances (36MB each, 40% larger than Telum) plus 360MB L3 (vs 256MB prior), (3) core shrink enabling cache growth while maintaining area, (4) microarch improvements: branch prediction, I-cache prefetch, additional rename registers, TLB optimization, (5) fully coherent multi-drawer architecture (up to 32 CP chips via drawer interconnects).

## The Key Experiment

- **speedup:** 5.5GHz frequency
- **other:** 600mm² die, 43B transistors, 8 cores/CP, 2.88GB L4 per drawer (up from 2GB z16)

**Compared against:** Prior Telum / z16 microprocessors

**Hardware:** CPU · **Workloads:** database; ai-inference; general-enterprise

## Why This Approach

Integration of Data Processing Unit (DPU) with enhanced cache hierarchy and improved core microarchitecture enabling both high single-thread performance and on-chip AI/data acceleration.

This paper sits in the **memory hierarchy** subtheme. The core constraint: compute starves waiting for data — arithmetic throughput far outpaces DRAM bandwidth. This paper's solution: New on-die Data Processing Unit (DPU) for AI acceleration and data processing.

## What It Leaves Open

- Not discussed.

**Tags:** ibm-z-telum, enterprise-processor, data-processing-unit, high-cache, 5nm, high-frequency
