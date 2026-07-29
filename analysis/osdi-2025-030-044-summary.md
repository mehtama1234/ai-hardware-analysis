# OSDI 2025 Papers 030-044: Thematic Analysis

Analysis of 15 consecutive OSDI papers spanning hardware acceleration, systems optimization, and distributed infrastructure.

## Theme Distribution

- **T1 (Attention/LLM Serving)**: 1 paper
- **T2 (Quantization)**: 1 paper  
- **T3 (Memory)**: 1 paper
- **T4 (Interconnect/Networking)**: 3 papers
- **T5 (Sparsity)**: 1 paper
- **T6 (Compiler/Tensor Programs)**: 1 paper
- **T7 (Security/Privacy)**: 1 paper
- **T9 (Specialized/Quantum)**: 1 paper
- **T0 (Systems/Infrastructure)**: 5 papers

---

## T1: LLM Serving & Attention (1 paper)

### DecDEC: A Systems Approach to Advancing Low-Bit LLM Quantization (osdi-2025-030)

**Problem**: Aggressive 3-4 bit quantization degrades LLM quality despite memory savings.

**Innovation**: Dynamic residual correction targeting activation outlier channels. Stores full-precision residual matrix in CPU, fetches residuals only for salient channels (identified by activation outliers) at each decoding step. Adapts to dynamic activation distributions rather than static channel importance.

**Impact**: 3-bit Llama-3-8B-Instruct: 10.15 → 9.12 perplexity (outperforms 3.5-bit) with <0.0003% GPU memory overhead and only 1.7% latency slowdown.

**Key Insight**: Decoupling static compression from dynamic error correction enables aggressive quantization without quality degradation. Activation-driven salient channel selection captures the dynamic nature of LLM inference.

---

## T2: Quantization (1 paper)

### DecDEC (see T1)

---

## T3: Memory Hierarchy & Disaggregation (1 paper)

### FineMem: Breaking Allocation Overhead vs. Memory Waste Dilemma (osdi-2025-039)

**Problem**: Disaggregated memory requires choosing between coarse-grained (low overhead, high waste) and fine-grained (low waste, high overhead) allocation strategies.

**Innovation**: Adaptive granularity that dynamically switches strategies based on runtime allocation patterns, learning when to aggregate vs. split allocations.

**Key Insight**: Traditional static allocation granularity is fundamentally suboptimal; adaptive strategies that respond to workload phase behavior achieve better overall efficiency.

---

## T4: Interconnect & Communication (3 papers)

### 1. FuseLink: Efficient GPU Communication over Multiple NICs (osdi-2025-032)

**Problem**: Static GPU-NIC bindings create bottlenecks at hot-spot NICs when ML workloads have imbalanced communication patterns (LLM serving, mixture-of-experts, recommendation systems).

**Innovation**: GPU-based traffic relay over intra-server connections to dynamically balance load across multiple NICs. Extends NCCL seamlessly without code modifications.

**Impact**: 
- 212 GBps inter-server GPU bandwidth
- 1.04-2.73x first-token latency reduction for LLM serving
- 1.3x MoE training throughput improvement
- 1.2x recommendation model training acceleration

**Key Insight**: Treating GPUs as network relay nodes converts static multi-NIC topology into dynamic load-balanced fabric, solving imbalanced traffic problem at application level.

### 2. Disentangling the Dual Role of NIC Receive Rings (osdi-2025-031)

**Problem**: NIC receive rings have dual responsibilities (buffering and scheduling) whose interactions are poorly understood and suboptimally optimized.

**Innovation**: Decouples buffering and scheduling roles, enabling independent optimization of each function.

**Key Insight**: Separating concerns in NIC architecture enables targeted performance optimization.

### 3. Söze: One Network Telemetry Is All You Need (osdi-2025-041)

**Problem**: Weighted bandwidth allocation for large-scale cloud networks requires per-flow knowledge, topology information, or routing details, making systems inflexible and hard to scale.

**Innovation**: Decentralized weighted bandwidth allocation using only commodity switch telemetry (queue depths, drop rates) without per-flow, topology, or routing knowledge.

**Impact**: 0.59x-0.79x TPC-H job completion time improvement. Scales to millions of flows without per-flow state.

**Key Insight**: Simple, local telemetry features from commodity switches suffice for globally-effective bandwidth allocation when proper inference is applied. Enables stateless, scalable control.

---

## T5: Sparsity & Mixture-of-Experts (1 paper)

### ZEN: Empowering Distributed Training with Sparsity-driven Synchronization (osdi-2025-042)

**Problem**: Distributed training communication bottlenecked by full gradient synchronization even when gradients are sparse (e.g., in pruned networks).

**Innovation**: Sparsity-aware communication primitives that skip zero gradients and compress sparse updates. Adaptive sparsity thresholds based on network conditions.

**Key Insight**: Exploiting gradient sparsity as a first-class optimization in communication layer, not just at computation level, reduces synchronization overhead significantly.

---

## T6: Compiler & Tensor Programs (1 paper)

### Mirage: A Multi-Level Superoptimizer for Tensor Programs (osdi-2025-043)

**Problem**: Tensor programs have enormous optimization search spaces spanning kernel-level, thread-block-level, and thread-level transformations. Existing optimizers miss cross-level optimizations.

**Innovation**: 
- μGraphs: unified representation of tensor programs at all GPU hierarchy levels
- Multi-level optimization combining algebraic, schedule, and kernel-generation transformations
- Abstraction-based pruning with optimality guarantees
- Probabilistic equivalence verification for correctness

**Impact**: Up to 3.3x speedup over existing approaches even on heavily-optimized DNNs.

**Key Insight**: Unified cross-level representation enables discovery of non-obvious multi-level optimizations that single-level optimizers miss. Abstraction-based pruning keeps search tractable while maintaining guarantees.

---

## T7: Security & Privacy (1 paper)

### Weave: Efficient and Expressive Oblivious Analytics at Scale (osdi-2025-036)

**Problem**: Oblivious analytics (hiding access patterns from adversaries) is necessary for privacy-sensitive applications but existing approaches are too slow for practical deployment.

**Innovation**: Algorithm-hardware co-design combining efficient oblivious data structures with distributed execution to hide access patterns at scale.

**Key Insight**: Privacy-preserving systems require joint optimization of algorithms and hardware to be practical.

---

## T9: Specialized Silicon & Non-NVIDIA (1 paper)

### Quantum Virtual Machines (osdi-2025-038)

**Problem**: Quantum computing requires robust virtualization to abstract hardware variability and enable portable quantum program execution across diverse processors with different capabilities.

**Innovation**: Quantum Virtual Machines providing abstraction layer for logical-to-physical mapping, handling qubit allocation, gate compilation, and error mitigation transparently.

**Key Insight**: Hardware abstraction is essential for emerging computing paradigms (quantum) to achieve portability and resilience to hardware variations.

---

## T0: Systems & Infrastructure (5 papers)

### 1. Mako: Speculative Distributed Transactions with Geo-Replication (osdi-2025-034)

**Problem**: Geo-replicated distributed transactions incur high commit latency due to synchronous coordination across replicas.

**Innovation**: Speculative transaction execution with rollback mechanisms for conflict recovery. Optimized for workloads with low abort rates.

**Key Insight**: Speculative execution can reduce latency in systems where conflicts are rare.

### 2. XSched: Preemptive Scheduling for Diverse XPUs (osdi-2025-035)

**Problem**: Heterogeneous accelerators have different scheduling models and preemption capabilities, requiring per-accelerator custom solutions.

**Innovation**: Abstraction layer for unified preemptive scheduling across heterogeneous accelerators with device-specific preemption handling.

**Key Insight**: Abstraction enables unified control across hardware diversity.

### 3. Scalio: DPU-based JBOF Key-value Store with NVMe-oF Offload (osdi-2025-037)

**Problem**: DPU-accelerated key-value stores lose acceleration benefits when NVMe management falls back to CPU.

**Innovation**: Offloads NVMe-oF target operations directly to DPU hardware, enabling end-to-end storage management without CPU involvement.

**Key Insight**: Enabling specialized processors to manage their own I/O eliminates the CPU bottleneck in heterogeneous systems.

### 4. Omniglot: Safe Interactions with Foreign Languages (osdi-2025-033)

**Problem**: Foreign Function Interfaces between managed and native code create safety risks with significant performance overhead.

**Innovation**: Safe FFI framework with automated validation through static analysis and lightweight runtime checks.

**Key Insight**: Principled cross-language abstraction design prevents safety violations while maintaining performance.

### 5. OS Rendering Service with Out-of-Order Execution (osdi-2025-044)

**Problem**: OS rendering services are traditionally sequential, limiting parallelism.

**Innovation**: Out-of-order execution with in-order commit for rendering: parallel speculative execution with ordered result commitment.

**Key Insight**: Weak ordering guarantees can be sufficient for many applications, enabling parallelism without full synchronization.

---

## Cross-Cutting Observations

### 1. Dynamic Adaptation vs. Static Optimization
Multiple papers demonstrate the power of runtime adaptation:
- **DecDEC**: Dynamic channel selection based on activation patterns
- **FineMem**: Adaptive allocation granularity
- **ZEN**: Adaptive sparsity thresholds
- **Söze**: Stateless control with dynamic telemetry

**Pattern**: Static designs often assume worst-case or average workloads; systems tuned to dynamic patterns unlock significant improvements.

### 2. Decoupling & Abstraction
Solving hard problems by decomposing concerns:
- **FuseLink**: Decouples GPU communication from static NIC assignments
- **Disentangling NIC Receive Rings**: Decouples buffering from scheduling
- **FineMem**: Decouples allocation decisions from granularity
- **XSched**: Abstracts heterogeneous preemption models
- **Omniglot**: Abstracts cross-language boundaries safely

**Pattern**: Tight coupling of concerns creates optimization obstacles; decoupling enables independent optimization and composability.

### 3. Hardware-Algorithm Co-design
Efficient systems require simultaneous optimization of both layers:
- **DecDEC**: Algorithm (outlier detection) + system (CPU residual storage)
- **Mirage**: Algorithm (multi-level transformations) + hardware (GPU hierarchy model)
- **Weave**: Algorithm (oblivious structures) + hardware (privacy-preserving compute)
- **Scalio**: Software (NVMe-oF) + hardware (DPU NVMe support)

**Pattern**: Single-layer optimization hits diminishing returns; joint design exploits hardware capabilities and algorithm properties.

### 4. Telemetry-Driven Decentralization
Systems using local information to coordinate globally:
- **Söze**: Switch telemetry for bandwidth allocation
- **FuseLink**: Per-NIC load information for relay decisions

**Pattern**: Modern systems avoid expensive centralized coordination; local, low-overhead signals enable distributed decision-making.

### 5. Speculative Execution
When conflicts/aborts are rare, speculation pays off:
- **DecDEC**: Speculatively fetch residuals for likely outlier channels
- **Mirage**: Speculatively optimize with rollback to verify correctness
- **Mako**: Speculatively commit transactions
- **OS Rendering**: Out-of-order speculative execution with ordered commit

**Pattern**: If abort/failure rates are low, the cost of speculation is amortized over many successful speculative steps.

---

## Emerging System Characteristics in This Batch

1. **Hierarchical Heterogeneity**: Papers tackle multi-level heterogeneity (GPU+CPU+NIC+DPU+quantum) requiring abstraction and coordination layers.

2. **Sparsity as First-Class Citizen**: From quantization residuals to sparse gradients to sparse matrix operations, sparsity-aware design appears across layers.

3. **Communication Optimization**: 3 out of 15 papers directly address communication (FuseLink, Söze, Disentangling NIC), reflecting growing recognition that communication, not computation, is the bottleneck in scale.

4. **Weak Ordering Suffices**: Multiple papers show that strict ordering is unnecessary; weak ordering properties sufficient for correctness enable parallelism (OS Rendering, Söze bandwidth).

5. **Quantum & Specialized**: Presence of quantum and DPU papers reflects 2025 hardware ecosystem diversification beyond GPU/CPU dominance.

---

## Relation to Broader 2025 Corpus

- **Theme alignment**: Papers lean heavily toward T0 (systems), T4 (interconnect), and emerging T9 (quantum), reflecting OSDI's systems-infrastructure focus vs. architecture-heavy venues.
- **LLM focus**: Only 1 paper (DecDEC) directly on LLM workloads, though FuseLink and ZEN serve LLM applications. OSDI balances workload-specific and general infrastructure work.
- **Hardware diversity**: Strong heterogeneity theme (GPUs, TPUs, DPUs, quantum) with multiple abstraction/coordination layers.
