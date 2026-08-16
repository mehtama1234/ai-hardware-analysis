# Co-Packaged Silicon Photonics Switches for Gigawatt AI Factories

**Venue:** HOTCHIPS
**Authors:** Gilad Shainer
**ID:** hotchips-2025-029
**Confidence:** low

## Problem
Large-scale AI cluster interconnects (many GPUs, CPUs in data centers) face power and latency limits with electrical switching; optical interconnects scale better but packaging and integration are challenging.

## Motivation
Gigawatt-scale AI factories require interconnects with extremely high bandwidth and low power; silicon photonics co-packaged with electronic switches offers superior scaling.

## Method
Instead of placing light-transmission components (waveguides that carry light signals, modulators that convert electrical signals to light, and detectors that convert light back to electricity) far from the electronic switch, they're built together in one package. This eliminates the long wires that would normally connect them, reducing power consumption and latency—the time signals take to travel.

## Key Novelty
Putting light-based optical components and electronic switch circuits in the same package reduces power consumption and latency for GPU cluster interconnects.

## Contributions
- Co-packaging of photonics and electronic switching logic
- Reduced power per bit vs pure electrical switching
- Low-latency optical interconnect for GPU-to-GPU
- Scalable architecture for Gigawatt-class AI clusters

## Hardware Target
- photonic
- GPU

## Technique Categories
- interconnect
- packaging

## Workloads
- LLM-training

## Metrics
- **bandwidth:** Tb/s
- **power:** per-bit efficiency

## Baselines
- Electrical switches (Infiniband, Ethernet)
- Pure optical interconnects

## Limitations
Specific performance numbers and integration details not in title.

## Tags
photonics, interconnect, ai-cluster, gpu, switching

## Primary Theme
Co-packaged silicon photonics for AI cluster interconnect
