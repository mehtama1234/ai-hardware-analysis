# Specialized IC for World-Lock Rendering in Augmented and Mixed Reality Devices

**Venue:** HOTCHIPS
**Authors:** Ohad Meitav, Jay Tsao
**ID:** hotchips-2025-023
**Confidence:** low

## Problem
AR/MR requires real-time rendering of virtual objects locked to the physical world, demanding high-frequency pose tracking and low-latency graphics; this cannot be done efficiently on mobile CPUs.

## Motivation
Consumer AR/MR devices (glasses, headsets) require on-device, real-time graphics rendering and spatial mapping to provide immersive experience without cloud latency.

## Method
The IC combines specialized vision (camera ISP, optical flow) and graphics engines optimized for tracking and rendering. It integrates pose estimation, world reconstruction, and graphics pipeline in silicon.

## Key Novelty
Specialized IC architecture combining vision and graphics for real-time world-locked AR rendering on mobile form factors.

## Contributions
- Integrated vision and graphics compute for AR rendering
- Real-time pose tracking and world reconstruction
- Low-power graphics pipeline for battery-constrained devices
- Optimized dataflow for world-lock consistency

## Hardware Target
- ASIC
- SoC

## Technique Categories
- circuit-design
- dataflow

## Workloads
- vision

## Metrics
- **latency:** pose-to-render time
- **power:** mobile device budget

## Baselines
- Mobile CPU rendering
- Mobile GPU rendering

## Limitations
Specific performance numbers and comparison with existing mobile GPUs not provided.

## Tags
ar, mr, rendering, mobile, vision

## Primary Theme
Specialized IC for real-time AR world-lock rendering
