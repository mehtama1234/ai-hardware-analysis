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
UB-mesh connects GPUs in a mesh topology—a grid-like pattern where each GPU links directly to its neighbors—instead of routing all data through central switches like traditional networks do. This reduces the distance (hop counts) data travels between GPUs and multiplies the total communication bandwidth available since many GPU pairs can communicate simultaneously over their direct connections. The switches and link speeds are optimized specifically for this mesh layout rather than being general-purpose.

## Key Novelty
UB-mesh replaces traditional switch-based interconnects with a mesh topology where GPUs connect in a grid pattern, reducing communication latency and increasing bandwidth density.

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
