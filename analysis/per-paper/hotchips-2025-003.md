# Passage M1000: A 3D Photonic Interposer for AI

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
Multi-chip AI systems suffer from electrical interconnect bottlenecks between processors and memory; photonic interconnects offer orders of magnitude higher bandwidth and lower energy per bit compared to electrical signaling.

## Motivation
AI accelerators and memory hierarchies face bandwidth saturation; optical interconnects can provide 10-100x higher bandwidth density at fraction of electrical power, enabling tighter chiplet integration.

## Method
Passage M1000 places a 3D optical routing layer—built from silicon photonics (technology that guides light like wires guide electricity)—between AI processor chips to replace or supplement electrical wires. It sends multiple signals at once using wavelength-division multiplexing (assigning each signal a different color of light), enabling far more data to travel between chips using less energy than electrical connections.

## Key Novelty
A 3D photonic interposer built from silicon photonics enables all-optical interconnects (light-based connections) between AI chips, replacing electrical wires.

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
