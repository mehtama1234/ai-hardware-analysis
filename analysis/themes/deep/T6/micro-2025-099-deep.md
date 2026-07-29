# MUSS-TI: Multi-level Shuttle Scheduling for Large-Scale Entanglement Module Linked Trapped-Ion

**Venue:** MICRO · **Subtheme:** Performance Scheduling & Autotuning

## What It Does

MUSS-TI constructs a dependency graph (DAG) of the quantum circuit and applies a multi-level scheduling strategy analogous to classical memory scheduling: storage zones map to L0 (disk), operation zones to L1 (memory), and optical zones to L2 (CPU). Gate selection prioritizes immediately executable gates; qubit routing assigns each qubit to the nearest-level available zone; conflict handling uses an LRU eviction policy to relocate the least-recently-used qubit to a lower-level zone. A look-ahead SWAP insertion algorithm (k=8 layers) strategically inserts SWAP gates between different QCCD modules to reduce long-range shuttle counts; a SABRE-inspired bidirectional initial mapping further reduces overhead.

Applying the multi-level cache scheduling abstraction (LRU replacement, zone-level hierarchy) to trapped-ion qubit routing, where storage/operation/optical zones are treated as memory levels and qubit eviction mimics page replacement.

## The Key Result

- **Speedup:** 58.9% shorter execution time vs. baseline for small-scale circuits
- **Other:** Shuttle operation reduction: 41.74% (30-32 qubits), 73.38% (117-128 qubits), 59.82% (256-299 qubits)

## Why This Approach

Multi-level shuttle scheduling framework (MUSS-TI) that maps EML-QCCD zones to memory hierarchy levels for efficient qubit routing. Zone-aware SWAP insertion algorithm using an 8-layer look-ahead weight table to reduce inter-QCCD shuttle operations. SABRE-based bidirectional initial qubit mapping adapted for EML-QCCD enhanced connectivity. Shuttle reduction of 41.74% (30-32 qubits), 73.38% (117-128 qubits), and 59.82% (256-299 qubits) vs. prior QCCD compilers, with 58.9% shorter execution time on small-scale benchmarks

This work addresses the fundamental problem: Compiling quantum circuits for Entanglement Module Linked Quantum Charge-Coupled Device (EML-QCCD) trapped-ion architectures is inefficient because existing compilers do not account for the distinct f...

## What It Leaves Open

- The evaluation uses simulation with a fidelity model rather than real hardware; the approach is specific to EML-QCCD and does not generalize to other modular quantum architectures such as superconducting or photonic chips.
