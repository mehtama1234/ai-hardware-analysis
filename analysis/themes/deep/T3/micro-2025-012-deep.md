# Stratum: System-Hardware Co-Design with Tiered Monolithic 3D-Stackable DRAM for Efficient MoE Serving

**Venue:** MICRO · **Theme:** Tiered 3D-Stacked PIM

## What It Does

MoE LLM inference is bottlenecked by the massive expert parameter volume (>95% of model size in models like Mixtral 8x7B), which overwhelms GPU HBM bandwidth and capacity; HBM-based NMP approaches are further limited by coarse-pitch TSV interconnects (~10 µm) that cap internal bandwidth.

Monolithic 3D-Stackable DRAM (Mono3D DRAM) enables Cu-Cu hybrid bonding at 1 µm pitch—5x finer than HBM TSVs—delivering higher internal bandwidth, but its aggressive vertical scaling introduces layer-dependent access latency heterogeneity that naive designs waste.

Stratum integrates Mono3D DRAM with NMP logic via Cu-Cu hybrid bonding on a logic die, connected to GPU via 2.5D silicon interposer. Within the Mono3D DRAM stack, an in-memory tiering mechanism assigns expert weights to fast (low wordline-staircase latency) or slow tiers based on predicted access frequency. A lightweight topic classifier predicts which experts will be hot for a given batch of user queries and re-maps them to fast tiers before each batch via a row-swap buffer. The NMP processor on the logic die includes per-channel Processing Units (PUs) connected via a ring network, each containing near-bank PE clusters with tensor cores executing GeMM/GeMV, an intra-channel reducer, and a SIMD special-function engine for Softmax/SiLU. The prefill phase runs on the GPU (xPU) and decoding runs on Stratum NMP.

## The Key Experiment

- **speedup:** up to 8.29x decoding throughput improvement vs. GPU baseline
- **energy or tops w:** up to 7.66x better energy efficiency vs. GPU baseline
- **area:** None
- **ppa:** None
- **accuracy:** None
- **other:** Mono3D DRAM internal bandwidth: ~5x higher vertical interconnect density than HBM (1 µm vs 10 µm TSV pitch)

**Compared against:** NVIDIA H100 GPU-HBM baseline; NVIDIA RTX A6000 GPU-HBM baseline; AttAcc; Neupims; Duplex

**Hardware:** GPU; PIM; chiplet · **Workloads:** LLM-inference; MoE; attention

## Why This Approach

In-memory tiering exploits inherent access-latency heterogeneity across Mono3D DRAM wordline layers, combined with topic-based expert usage prediction, to maximally concentrate hot expert weights in fast DRAM tiers without off-chip data movement.

This paper sits in the **memory hierarchy** subtheme. The core constraint: compute starves waiting for data — arithmetic throughput far outpaces DRAM bandwidth. This paper's solution: First system-hardware co-design for MoE serving using Monolithic 3D-Stackable DRAM, integrating 3D hybrid bonding with 2.5D silicon interposer.

## What It Leaves Open

- Mono3D DRAM is an emerging technology not yet in volume production
- evaluation is simulation-based and assumes projected device parameters that may differ from eventual silicon.

**Tags:** moe, llm-inference, near-memory-processing, 3d-dram, memory-tiering, chiplet
