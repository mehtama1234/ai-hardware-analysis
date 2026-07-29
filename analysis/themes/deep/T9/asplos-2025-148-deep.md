# Micro Blossom: Accelerated Minimum-Weight Perfect Matching Decoding for Quantum Error Correction

**Venue:** ASPLOS · **Subtheme:** Quantum Error Correction Acceleration

## What It Does

Micro Blossom accelerates the blossom algorithm—the classical exact solver for Minimum-Weight Perfect Matching (MWPM)—using a heterogeneous CPU+FPGA co-design. The FPGA instantiates one vertex processing unit (vPU) and one edge processing unit (ePU) per graph node and edge, partitioning the algorithm's primal (CPU-resident) and dual (hardware) phases. Each vPU maintains only local state (residue, unique-touch metadata, direction) and communicates via broadcast/convergecast network primitives with graph neighbors. The dual phase—which dominates MWPM latency—runs fully parallelized in hardware; isolated conflicts (the common case at low error rates) are detected and resolved entirely in hardware via parallel ePU logic, bypassing CPU interactions. Round-wise fusion processes each new measurement round incrementally as syndrome data arrives, achieving stream decoding with constant latency independent of the number of rounds.

The decoder achieves O(d³) parallel processing units for surface code distance d, with worst-case complexity reduced from O(d¹²) to O(d⁹). Hardware generation is automated from a JSON decoding-graph specification via SpinalHDL, producing synthesizable Verilog. The prototype runs on a Xilinx Versal VMK180 FPGA at 62 MHz.

## The Key Result

On a surface code at distance d=13 and physical error rate p=0.1%, Micro Blossom achieves average decoding latency of 0.8 microseconds, compared to 6.5 microseconds for Sparse Blossom on an Apple M1 Max CPU—an 8x latency reduction. Total logical error rate matches exact MWPM baselines (Parity Blossom), delivering 17x faster decoding than prior CPU implementations while maintaining correctness. The hardware architecture eliminates the O(p|V|) CPU interactions present in prior designs, reducing average-case complexity from O(pd³+1) to O(p²d²+1).

## Why This Approach

Fault-tolerant logical T-gates in superconducting qubits require decoder feedforward within ~1 microsecond; every microsecond of decoding latency multiplies the effective logical error rate by a factor of (1 + L/d), placing decoding latency on the critical path for practical fault-tolerant quantum computation. Prior exact MWPM decoders on CPUs achieve multi-microsecond latency, forcing the field to adopt approximate decoders that sacrifice accuracy (1.7x–13.9x more logical errors at d=13). The specialization to hardware enables fine-grained parallelization of the blossom algorithm's dual phase—previously thought too complex for acceleration—by decomposing it into per-vertex and per-edge processing units with only local connectivity, avoiding the global synchronization barriers that plague graph algorithms on CPUs.

## What It Leaves Open

- FPGA prototype runs at 62 MHz; ASIC implementation would enable 500+ MHz+ clock speeds and higher code distances for sub-100 ns latencies, but silicon results are absent
- Scalability to code distances d > 13 and higher physical error rates (p > 1%) requires more vPU/ePU resources; area scaling and placement feasibility unexplored
- Integration with real QEC controllers (e.g., Rigetti or atom-computing stacks) requires protocol standardization and latency-matched I/O buffers
- Multi-round graph updates (re-weighting edges as new syndromes arrive) may incur latency spikes not fully characterized in the stream-decoding model
- Generalization to other exact decoders (e.g., dual-space, tensor-network) outside the blossom family remains unclear
