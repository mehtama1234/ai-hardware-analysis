# Everactive: Self-Powered SoC with Energy Harvesting, Wakeup Receiver, and Energy-Aware Subsystem

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
Battery-powered IoT and edge devices suffer from limited lifetime; Everactive proposes a self-powered SoC that harvests ambient energy (RF, thermal, mechanical) to enable continuous operation without battery replacement.

## Motivation
IoT device deployment at scale requires minimizing maintenance and replacement costs; energy harvesting enables perpetual operation, critical for remote sensor networks and autonomous monitoring.

## Method
Everactive integrates energy harvesting circuits (RF rectifier, thermoelectric, piezoelectric), a wakeup receiver for low-power event detection, and an energy-aware subsystem that dynamically manages compute and memory based on harvested power availability.

## Key Novelty
Self-powered SoC architecture with integrated energy harvesting and dynamic power management enabling perpetual operation without battery.

## Contributions
- Integrated energy harvesting from RF, thermal, and mechanical sources
- Ultra-low-power wakeup receiver for event-driven activation
- Energy-aware runtime subsystem managing compute vs. stored energy
- Demonstrated perpetual operation on harvested power alone

## Hardware Targets
SoC, CPU

## Techniques
power, scheduling, circuit-design

## Workloads
database, speech

## Metrics
- Power: milliwatt-scale harvested power enabling perpetual operation
- Energy: sub-milliwatt average power consumption

## Baselines
Battery-powered IoT devices, Traditional ultra-low-power microcontrollers

## Limitations
Scalability to compute-intensive workloads and practical harvesting yields under real-world environmental variation not discussed.

## Tags
energy-harvesting, perpetual, iot, self-powered, low-power, edge
