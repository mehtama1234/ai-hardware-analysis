# Handling Latch Loops in Timing Analysis with Improved Complexity and Divergent Loop Detection

**Venue:** DATE · **Subtheme:** Timing Analysis

## What It Does

Identifies strongly connected components (SCCs) in timing graph, levelizes them into stages; parallelizes arrival time propagation between SCCs while performing sequential iterations within each SCC; detects divergent loops to avoid unnecessary iterations.

SCC-based approach reducing latch loop complexity from O(n²) to O(Σk_i²) with lookahead divergent loop detection.

## The Key Result

- **Speedup Vs Primetime:** 10.31×
- **Speedup Vs Opensta:** 8.77×

## Why This Approach

Complexity reduction from O(n²) to O(Σk_i²). 10.31× speedup over PrimeTime on average. 8.77× speedup over OpenSTA on average. Divergent loop detection avoiding over-iteration

This work addresses the fundamental problem: Latch loops introduce feedback cycles in timing graphs disrupting static timing analysis; existing timers require global iterations with worst-case O(n²) complexity where n is number of pins.

## What It Leaves Open

- Not discussed.
