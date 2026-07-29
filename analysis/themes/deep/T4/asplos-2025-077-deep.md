# Enhancing CGRA Efficiency Through Aligned Compute and Communication Provisioning

**Venue:** ASPLOS · **Subtheme:** Dataflow & NoC Optimization

## What It Does

Plaid addresses a fundamental inefficiency in Coarse-Grained Reconfigurable Arrays (CGRAs): existing designs pair each processing element with a full crossbar router to handle peak communication load, but in practice this router sits mostly idle. Instead of one router per PE, Plaid groups three ALUs into a Plaid Collective Unit (PCU) that shares a single lightweight local router handling all three-node communication patterns. These are exhaustive structural motifs discovered in dataflow graphs (fan-in, fan-out, unicast patterns) — recurring three-node subgraph structures. The PCU's local router handles all intra-motif data movement internally, while a global inter-PCU router connects different PCUs for longer-range communication. The Plaid compiler (built on the Morpher toolchain) automatically identifies motifs in kernel dataflow graphs, generates a hierarchical representation, and maps it onto the PCU array using flexible schedule templates that keep all three ALUs busy without buffering overhead.

The key mechanism is recognizing that a 4×4 spatial CGRA (16 PEs, 16 routers) and a 2×2 Plaid CGRA (6 PCUs = 18 ALUs, 6 local routers + 1 global router) have the same functional capacity but fundamentally different communication patterns. By accepting that computation rarely occurs in truly arbitrary patterns and mostly flows through small repeating three-node structures, Plaid replaces 16 full crossbars with 7 smaller routers, eliminating the per-PE overprovisioning that wastes area and power.

## The Key Result

On CNN, vision, and HPC workloads (30 kernels from TinyML, PolyBench, and image processing benchmarks), Plaid achieves 1.4× performance improvement over energy-efficient spatial CGRAs while matching the performance of high-performance spatio-temporal CGRAs. Energy-wise: 43% power reduction versus spatio-temporal CGRA; 27.7% energy reduction versus spatial CGRA; overall 42% total energy reduction versus spatio-temporal baseline. Area: 46% area savings versus spatio-temporal; 48% area savings versus spatial CGRA. PPA (power-performance-area): 1.22× energy efficiency and 1.25× area efficiency compared to domain-optimized spatio-temporal CGRA.

## Why This Approach

CGRAs are valued for domain-agility but historically pay a heavy price: communication hardware (routers, buffers, multiplexers) consumes 44% of power and 46% of area in spatio-temporal designs, yet achieves only modest average utilization because individual PEs rarely communicate with every other PE in every cycle. Plaid leverages the structural observation that most practical computation flows through small three-node patterns — no kernel naturally produces a uniform random communication matrix. By designing the collective unit around these motifs and letting the compiler identify them, Plaid achieves both the adaptability of spatial dataflow CGRAs and the efficiency of specialized accelerators. The alternative (hand-design per-workload or accept high overprovisioning) does not scale; Plaid generalizes across all dataflow kernels without manual per-architecture tuning.

## What It Leaves Open

- Kernels with very complex or long-distance data dependencies that cannot be captured by three-node motifs fall back to individual-node-to-node communication through the global router, losing the efficiency gain and potentially serializing across longer paths.
- No investigation of how memory hierarchy (scratchpad/register file organization) interacts with the PCU-based communication; assumes sufficient local buffering.
- Scalability to very large arrays (e.g., 16×16 PCUs) and whether motif density remains high in massive dataflow graphs is unexplored.
- Does not address reconfiguration time or dynamic re-mapping if workload phases demand different motifs; assumes static per-kernel mapping.
- Comparison limited to CGRAs; no evaluation against GPU tensor cores or specialized ML accelerators (Gemmini, TensorFlow TPU variants) on shared workloads.
