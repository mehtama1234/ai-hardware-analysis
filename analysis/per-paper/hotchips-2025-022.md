# FABRIC8LABS Electrochemical Additive Manufacturing ECAM Enabled Thermal Solutions for the Al Data Center

**Venue:** HOTCHIPS
**Authors:** Michael Matthews, Ian Winfield, Joseph Madril, Douglas De Aquino Castro, Charles Biset
**ID:** hotchips-2025-022
**Confidence:** low

## Problem
Data center cooling consumes significant power and space; traditional liquid and air cooling systems scale poorly as chip power density increases.

## Motivation
Power density of AI accelerators (TPUs, GPUs, specialized ASICs) has increased dramatically, requiring innovative thermal management to avoid cooling cost becoming dominant data center expense.

## Method
Electrochemical additive manufacturing (ECAM—a type of 3D printing) produces custom-shaped copper structures that attach directly to computer chips. Liquid coolant flows through these structures, absorbing heat at the source. The structures are designed to transfer heat efficiently while keeping pressure drop minimal, so the coolant moves freely.

## Key Novelty
Using electrochemical 3D printing to create custom-shaped copper cooling structures that attach directly to chips for optimized heat transfer.

## Contributions
- Electrochemical additive manufacturing for cooling structure fabrication
- Direct chip-to-liquid cooling improving thermal transfer
- Reduced cooling infrastructure cost and complexity
- Enables higher power-density chip deployment

## Hardware Target
- GPU
- ASIC
- TPU

## Technique Categories
- power
- packaging

## Workloads
- LLM-training

## Metrics
- **thermal_resistance:** °C/W
- **power_density:** W/mm²

## Baselines
- Traditional liquid cooling
- Air cooling systems

## Limitations
Specific thermal performance numbers and long-term reliability data not discussed.

## Tags
thermal, cooling, manufacturing, data-center, ecam

## Primary Theme
Advanced manufacturing for data center cooling
