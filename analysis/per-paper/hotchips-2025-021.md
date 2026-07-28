# UB-mesh: An New Interconnection Technology for Large AI SuperNode

**Venue:** HOTCHIPS
**Authors:** Heng Liao
**ID:** hotchips-2025-021
**Confidence:** low

## Problem
Scaling AI clusters with many GPUs requires very-high-bandwidth, low-latency interconnects; current PCIe and traditional switch fabrics limit all-to-all communication for distributed training.

## Motivation
Large-scale AI training (LLMs, multimodal models) demands dense GPU interconnects to minimize communication bottlenecks and improve scaling efficiency.

## Method
UB-mesh proposes a custom mesh-topology interconnect optimized for GPU clusters. It likely includes novel switching logic, reduced hop counts, and optimized link speeds compared to traditional Ethernet/Infiniband.

## Key Novelty
Custom mesh-based interconnection architecture reducing latency and increasing bandwidth density for large GPU clusters.

## Contributions
- Mesh-topology interconnect design for GPU clusters
- Low-latency communication primitives for collective operations
- Bandwidth density improvements vs Ethernet/Infiniband
- Scalable architecture supporting large supernode deployment

## Hardware Target
- GPU
- interconnect

## Technique Categories
- interconnect

## Workloads
- LLM-training
- LLM-inference

## Metrics
- **bandwidth:** GPU-GPU links
- **latency:** hop delay

## Baselines
- Infiniband
- PCIe 5.0
- Ethernet

## Limitations
Technical details on topology, link speeds, and comparative performance not in title.

## Tags
interconnect, gpu-cluster, ai-training, supernode, mesh

## Primary Theme
Custom mesh interconnect for AI GPU clusters
