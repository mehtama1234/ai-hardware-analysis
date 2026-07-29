# Finesse: An Agile Design Framework for Pairing-based Cryptography via Software/Hardware Co-Design

**Venue:** ISCA · **Subtheme:** Cryptographic Acceleration (Pairing-based)

## What It Does

Finesse is a design framework for pairing-based cryptography (PBC) accelerators that abstracts away hardware pipeline details. It uses a three-layer abstraction: (1) intermediate representation (IR) for finite-field operations and their dependencies, (2) a pipeline template with reconfigurable issue slots, and (3) issue-slot affinity scheduling. Designers specify PBC algorithms (e.g., Ate pairing, BLS signatures) in the IR—a DAG of field multiplications, additions, and squarings. Finesse then compiles the IR to a pipeline by: (a) grouping operations into issue slots (periodic 4–8 cycle intervals), (b) assigning operations via affinity scheduling to slots that minimize stalls and structural hazards, and (c) generating Verilog pipelines with variable-latency units.

Data path: operand fetch → issue slot i (delay-matched to Long Latency Multipliers) → issue slot i+1 (addition/squaring) → result writeback. The scheduler respects hardware constraints (e.g., multiplier occupancy) by mapping dependent chains across multiple pipeline stages.

## The Key Result

Finesse designs pairing accelerators with 1.8x–3.2x better throughput than hand-optimized pipelines and 2.4x faster design-space exploration (6 hours vs. 1–2 weeks manual). A BLS signature unit achieves 1.2 KOPS (1,200 signatures/sec) on 120 nm technology compared to 200 KOPS for Synopsys-optimized designs—Finesse is slightly slower but enables rapid re-design for emerging curves (BN-254 → BLS12-381 → CP6_6). Reconfigurability allows the same silicon to support three pairing variants with <5% area overhead.

## Why This Approach

Pairing-based cryptography (used in zkSNARKs, threshold cryptography, functional encryption) requires frequent re-engineering as security standards evolve (BN-254 deprecated, BLS12-381 preferred, new curves discovered). Hand-tuned pipelines take weeks to design because pairing requires 50+ field multiplications in exact dependency order, and pipeline stalls cascade if dependencies are misscheduled. Finesse's issue-slot affinity scheduling automatically maps dependencies to hardware slots, reducing design time from 2 weeks to 6 hours. The abstraction layer insulates designers from low-level Verilog details.

## What It Leaves Open

- Performance still 2x–3x slower than vendor-optimized ASIC designs; Finesse trades performance for retargetability
- Scaling to ultra-high-frequency (>1 GHz) pipelines requires deeper pipelining; affinity scheduling heuristics for deeper pipelines not explored
- Non-arithmetic operations (comparisons, conditional jumps) poorly supported; structured PBC algorithms assume mostly arithmetic chains
- Post-silicon tuning and power optimization not addressed; reconfigurable pipelines may waste power through unused stages
- Generalization to other algebraic structures (ECC, RSA, lattices) requires new IR abstractions; unclear if framework scales beyond pairing
