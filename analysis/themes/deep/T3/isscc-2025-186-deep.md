# IRIS: A 8.55mJ/frame Spatial Computing SoC for Interactable Rendering and Surface-Aware Modeling with 3D Gaussian Splatting

**Venue:** ISSCC · **Theme:** Spatial Computing SoC

## What It Does

Interactive Spatial Computing (ISC) for mixed-reality (MR) requires real-time surface-aware modeling (SAM) and interactive photorealistic rendering (IPR) with tight latency budgets (15ms) and high computational demands. 3D Gaussian Splatting (3DGS) enables superior quality but faces three challenges: (1) massive external memory access (EMA) for unordered >50MB parameters exceeds edge GPU L2 cache (4MB), (2) IPR requires three sequential stages (deform/reflect/render) causing 2.33x overhead vs. non-interactive rendering, (3) backpropagation for SAM consumes 55.8% of compute due to FP16 precision and limited reusability.

Mixed-reality applications demand immersive, deformable 3D object manipulation in real-time on mobile/edge devices; NeRF accelerators cannot support surface extraction and deformation required for ISC, necessitating specialized 3DGS hardware.

IRIS SoC implements Single-Embedding-Multi-MLP (SEMM)-based 3DGS compression reducing parameter size while preserving quality. The architecture features specialized datapath for SAM and IPR stages, optimized memory hierarchy to minimize EMA, and hardware reuse for backpropagation to reduce compute redundancy. Spatial computing-aware scheduling and memory orchestration keep all processing within tight 15ms latency budget.

## The Key Experiment

- **energy or tops w:** 8.55mJ/frame
- **speedup:** 15ms latency for interactive rendering
- **other:** SAM: <20min (vs >20min on edge GPU), IPR: <400ms (vs >400ms baseline)

**Compared against:** Jetson Orin Nano edge GPU; NeRF accelerators

**Hardware:** SoC; ASIC · **Workloads:** vision; 3d-graphics; neural-rendering

## Why This Approach

First specialized edge SoC for interactive 3DGS-based MR, achieving 8.55mJ/frame through MLP-based compression and co-optimized SAM/IPR/backprop pipelines.

This paper sits in the **memory hierarchy** subtheme. The core constraint: compute starves waiting for data — arithmetic throughput far outpaces DRAM bandwidth. This paper's solution: SEMM-based 3DGS compression reducing EMA from 81.3% to 52.8% of system energy.

## What It Leaves Open

- Not discussed.

**Tags:** 3d-gaussian-splatting, mixed-reality, spatial-computing, edge-soc, neural-rendering, real-time-graphics
