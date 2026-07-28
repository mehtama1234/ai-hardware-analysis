# KLIMA: Low-latency mixed-signal In-Memory Computing accelerator for solving arbitrary-order Boolean Satisfiability

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
Boolean Satisfiability (SAT) solving requires exploring vast search spaces, with conventional CPU/GPU approaches suffering from memory bandwidth and latency bottlenecks. KLIMA addresses solving arbitrary-order SAT problems with single-digit nanosecond latency.

## Motivation
SAT solving is a fundamental NP-complete problem critical for formal verification, cryptanalysis, and combinatorial optimization, but conventional digital approaches struggle with the memory-latency wall.

## Method
KLIMA uses mixed-signal in-memory computing (analog logic with digital interfacing) to perform SAT clause evaluation in memory, eliminating von Neumann bottlenecks by computing directly on stored data using current-mode analog circuits that evaluate Boolean expressions faster than digital logic can fetch operands.

## Key Novelty
Analog in-memory Boolean circuits combined with low-latency mixed-signal interfacing to achieve native SAT solving directly in the memory substrate.

## Contributions
- Mixed-signal IMC architecture for native SAT solving with nanosecond-scale latency
- Support for arbitrary-order Boolean clauses without serial evaluation
- Elimination of memory-latency bottleneck through analog compute-in-memory
- Demonstrated speedup over conventional SAT solvers on large search spaces

## Hardware Targets
ASIC, CIM

## Techniques
near-data-processing, approximation, circuit-design

## Workloads
cryptography

## Metrics
- Latency: single-digit nanoseconds
- Energy: reduced memory bandwidth vs. CPU/GPU

## Baselines
CPU SAT solvers, GPU SAT solvers

## Limitations
Unclear scalability to modern large SAT instances; analog circuit noise tolerance and technology cost not discussed.

## Tags
imc, sat-solving, analog-logic, low-latency, verification, cryptography
