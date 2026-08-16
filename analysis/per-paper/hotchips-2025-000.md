# KLIMA: Low-latency mixed-signal In-Memory Computing accelerator for solving arbitrary-order Boolean Satisfiability

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
Boolean Satisfiability (SAT) solving requires exploring vast search spaces, with conventional CPU/GPU approaches suffering from memory bandwidth and latency bottlenecks. KLIMA addresses solving arbitrary-order SAT problems with single-digit nanosecond latency.

## Motivation
SAT solving is a fundamental NP-complete problem critical for formal verification, cryptanalysis, and combinatorial optimization, but conventional digital approaches struggle with the memory-latency wall.

## Method
KLIMA solves SAT problems by evaluating Boolean clauses directly in memory using mixed-signal circuits—combining analog logic with digital interfaces. Rather than moving data between memory and a separate processor, current-mode analog circuits stay in memory and compute using electrical current flow, which evaluates expressions faster than digital logic can fetch them. This in-memory computing approach eliminates the traditional von Neumann bottleneck (the slowdown from shuttling data back and forth) and achieves single-digit nanosecond latency for arbitrary-order SAT problems.

## Key Novelty
KLIMA embeds analog circuits directly in memory to evaluate Boolean expressions for SAT solving, bypassing the need to move data to a processor.

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
