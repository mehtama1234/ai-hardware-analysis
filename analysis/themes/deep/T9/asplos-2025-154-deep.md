# Fat-Tree QRAM: A High-Bandwidth Shared Quantum Random Access Memory for Parallel Queries

**Venue:** ASPLOS · **Subtheme:** Quantum Memory Architectures

## What It Does

Fat-Tree QRAM replaces the single router node in Bucket-Brigade (BB) QRAM with a Fat-Tree topology, enabling query-level pipelining in photonic/analog quantum systems. In classical BB QRAM, a single binary tree routes measurement requests sequentially through O(log N) layers. Fat-Tree QRAM inserts multiple parallel routers at each level; a hierarchical scheduler selects non-conflicting memory addresses to launch in parallel through different tree branches. The architecture achieves O(log N) query-level pipelining within O(log N) circuit depth by separating the physical depth (log N for single-tree traversal) from the scheduling depth (additional log N routing decisions) and exploiting parallelism across independent address spaces.

Data flow: incoming queries arrive at the root, route through the fat-tree fabric (parallel branches at each level), and reach memory elements in time O(log N). Subsequent queries pipeline behind the first via scheduler-coordinated branch allocation. The system maintains query order via age-based prioritization in the scheduler.

## The Key Result

Fat-Tree QRAM achieves O(log N) query latency with O(log N) circuit depth (query-level pipelining), compared to BB QRAM's sequential latency O(N) or O(log² N) with deeper pipelines. On a 64-qubit register (N=2⁶⁴), Fat-Tree overlaps 64 queries in-flight simultaneously, reducing time-to-solution for algorithms requiring repeated memory access (e.g., Grover search) by up to 64x compared to sequential BB QRAM, while maintaining the O(log N) photonic circuit depth advantage over classical random-access memory.

## Why This Approach

Existing QRAM architectures bottleneck on sequential query processing: each memory access serializes through a single tree, forcing wait times of O(N) or O(log² N) even in optimized designs. This serialization is the critical bottleneck for algorithms requiring many queries (Grover search, HHL linear systems). Fat-Tree QRAM enables query-level parallelism—fundamental to Quantum computing—by decoupling physical depth (log N tree traversal) from scheduling depth (log N independent routing decisions). Photonic systems benefit most because optics enable massive fan-in/fan-out and parallel wavelength channels naturally.

## What It Leaves Open

- Photonic implementation complexity: no silicon results; experimental demonstration on actual photonic platforms (e.g., Xanadu, Atom Computing photonics) pending
- Scaling to N > 2⁶⁴ or ultra-low-latency regimes (nanosecond clocks) requires denser photonic integration and phase-management protocols not yet characterized
- Error correction for photonic memory elements and routing fidelity not addressed; assumes ideal quantum channels
- Scheduling policy fairness and worst-case query latency variance under contention not fully specified
- Integration with real photonic quantum processors (trapped-ion, superconducting photonic hybrids) unclear
