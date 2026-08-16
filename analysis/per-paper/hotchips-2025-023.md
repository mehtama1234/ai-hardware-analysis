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
The chip contains specialized circuits for vision processing and graphics rendering that work together. The vision engine analyzes camera images using optical flow (detecting motion through pixel changes) to track the device's position and reconstruct the physical environment in 3D. The graphics engine simultaneously renders virtual objects based on this tracking data. Because tracking, mapping, and rendering all happen on dedicated silicon instead of the general-purpose CPU, the system achieves the low latency required for AR/MR.

## Key Novelty
A custom hardware chip combines vision tracking and graphics rendering on the same silicon, enabling real-time world-locked rendering on mobile devices.

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
