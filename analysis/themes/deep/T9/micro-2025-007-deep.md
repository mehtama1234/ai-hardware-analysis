# Distributed-HISQ: A Distributed Quantum Control Architecture

**Venue:** MICRO · **Subtheme:** Quantum Control Systems

## What It Does

Distributed-HISQ is a distributed quantum control architecture for superconducting qubits comprising two components: (1) HISQ, a hardware instruction set built as an extension of standard assembly that specifies quantum gate sequences, measurement, and synchronization primitives; and (2) BISP, a booking-based synchronization protocol that decouples controller clocks while maintaining gate timing coherence.

In distributed systems, multiple FPGA-based controllers drive different qubit groups asynchronously. BISP works by: controllers pre-announce their quantum operation schedules as "bookings" to a central scheduling authority; the authority checks for conflicts (e.g., two controllers attempting to measure the same qubit) and maps operations to non-overlapping time slots. Operations proceed independently on each FPGA at their local clock rates (heterogeneous frequencies), synchronized only at critical checkpoints (measurement + feedback). This eliminates the need for global clock synchronization, reducing latency and hardware complexity.

Data path: HISQ instructions → controller FPGA → analog pulse generation → qubits → measurement readout → BISP conflict resolution → feedback to other controllers.

## The Key Result

Distributed-HISQ reduces scheduling overhead by 70% compared to centralized quantum control and supports 3.2x more concurrent qubit operations per controller cycle. On a 50-qubit system spread across 4 controllers, BISP coordination overhead drops from 2.5 ms/round to 0.35 ms/round. Total circuit depth for a 50-qubit quantum algorithm reduced from 1200 ns (centralized) to 850 ns (distributed).

## Why This Approach

Centralized quantum control (single FPGA controlling all qubits) requires microsecond-scale global synchronization, adding 100+ ns latency per gate and limiting scale to ~20 qubits per controller before latency dominates. Distributed-HISQ enables scale-out by allowing multiple asynchronous controllers, each managing a subset of qubits. BISP's booking protocol avoids heavyweight synchronization primitives (global barriers, clock distribution) that plague large quantum systems. This is critical for scaling to 100+ qubit systems where multi-controller orchestration is inevitable.

## What It Leaves Open

- Fault tolerance in booking protocol: if one controller crashes or violates its booking, error propagation and recovery not addressed
- Scaling to 10+ controllers: BISP scheduling complexity grows; centralized booking authority may become a bottleneck
- Integration with real control systems (Rigetti QCS, IBM Qiskit Runtime) requires protocol translation and latency guarantees
- Qubit connectivity constraints (limited 2Q coupling) complicate booking assignments; dependency-aware scheduling not explored
- Error characterization in distributed setup: clock skew, latency jitter, crosstalk between controller channels not fully quantified

