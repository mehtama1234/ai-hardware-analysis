# Passage M1000: A 3D Photonic Interposer for AI

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
Multi-chip AI systems suffer from electrical interconnect bottlenecks between processors and memory; photonic interconnects offer orders of magnitude higher bandwidth and lower energy per bit compared to electrical signaling.

## Motivation
AI accelerators and memory hierarchies face bandwidth saturation; optical interconnects can provide 10-100x higher bandwidth density at fraction of electrical power, enabling tighter chiplet integration.

## Method
Passage M1000 uses a 3D photonic interposer with integrated silicon photonics to route optical signals between chiplets, replacing or supplementing electrical interconnects with wavelength-division multiplexing (WDM) to achieve massive bandwidth on a single optical layer.

## Key Novelty
3D photonic interposer technology enabling all-optical chiplet interconnects with silicon-photonics integration for AI systems.

## Contributions
- 3D photonic interposer architecture for chiplet-to-chiplet communication
- Silicon photonics integration enabling compact optical routing
- High-bandwidth, low-energy chiplet interconnects replacing electrical traces
- Demonstrated multi-chiplet AI system integration

## Hardware Targets
photonic, chiplet, ASIC

## Techniques
interconnect, packaging, parallelism

## Workloads
LLM-training, LLM-inference

## Metrics
- Speedup: reduced latency in multi-chip communication
- Energy: orders of magnitude lower energy per bit vs. electrical

## Baselines
Electrical interposers, HBM stacking, chiplet interconnects

## Limitations
Scaling to production volume, photonics-to-electronics integration challenges, and real-world AI workload validation not discussed.

## Tags
photonic, interconnect, chiplet, bandwidth, 3d-integration, silicon-photonics
