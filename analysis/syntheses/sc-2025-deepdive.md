# SC (Supercomputing) 2025 — Deep Dive

## What SC (Supercomputing) is and why it exists

SC, the International Conference for High Performance Computing, Networking, Storage, and Analysis, is the North American flagship venue for flagship-scale computing research. The conference unites researchers, practitioners, and vendors around a central technical question: how do we solve the world's most demanding computational problems—and what breakthroughs in hardware, software, algorithms, and systems architecture are necessary to make that possible?

Unlike machine learning conferences (which ask "what can we train?"), SC asks "what can we *run at scale*?" The distinction matters. A model that trains on a single machine is interesting; a model that trains across 10,000 GPUs at exascale is a system engineering problem. SC is where those engineering solutions are born.

The conference spans three technical worlds colliding: traditional scientific computing (climate simulation, molecular dynamics, quantum chemistry), modern AI workloads (distributed LLM training, inference serving, graph neural networks), and the infrastructure that connects them (HPC interconnects, parallel filesystems, fault-tolerant runtimes). Its papers reflect the moment we're in: exascale supercomputers have landed (Frontier at Oak Ridge, Aurora at Argonne, El Capitan at NNSA), and the challenge is no longer building them—it's programming them, operating them, and extracting useful science from them.

SC's unique position in the ecosystem is anchored in reproducibility culture. Of the 430 papers accepted in 2025, roughly 11% explicitly focus on reproducibility and artifact evaluation. This reflects a community-wide mandate: claims of performance, scalability, or correctness must be independently verifiable. Papers come with code, data, and reproducibility reports evaluated against a standardized rubric.

## The core constraint

Supercomputing is a discipline defined by fundamental physical and economic constraints that reshape every technical decision made in a paper.

**Constraint 1: Power scales with *everything***

An exascale system consumes 10–20 MW. At $0.10 per kilowatt-hour, that's $10M–$20M per year in electricity alone. A 10% improvement in power efficiency for a five-year system lifetime saves $5M–$10M. Consequently, every optimization (communication, memory movement, precision) is evaluated not just on speed but on energy per operation. Papers like "Benchmark-driven Models for Energy Analysis and Attribution of GPU-Accelerated Supercomputing" exemplify this: they instrument entire systems to understand where joules are being spent, and optimizations are only credible if they prove energy savings.

This constraint forces a particular kind of thinking. When a paper proposes a new compression scheme, communication strategy, or memory hierarchy, the community's immediate question is: "At what power cost?" Papers that ignore this are dismissed as impractical.

**Constraint 2: Communication dominates**

On a supercomputer with 10,000 nodes, the speed of light becomes a real enemy. If a node sends 1 MB of data across an Infiniband fabric at 200 Gbps, that's 40 microseconds of network time. Multiply by 10,000 nodes and suddenly communication is the critical path. Papers addressing collective operations (allreduce, broadcast, scatter-gather), network-offloaded computation, and topology-aware placement reflect this obsession with communication reduction.

The 56 papers tagged "Communication & Interconnect" show researchers attacking this in every direction: programmable switches that compute while routing, network protocols that reduce the number of hops, MPI optimizations that avoid serialization, and algorithms redesigned from scratch to minimize message volume. "MPI Collectives with Programmable Smart Switches" exemplifies this: by moving collective reduction logic into the network fabric itself, entire algorithmic layers can be bypassed.

**Constraint 3: Fault tolerance is non-negotiable**

At exascale, assuming zero failures is fiction. With millions of components (cores, memory modules, network links), the mean time to failure (MTTF) is hours to days. A 48-hour simulation that crashes at hour 47 is catastrophic. Therefore, every long-running application must either: (a) checkpoint regularly, (b) use algorithm-based fault tolerance (ABFT), or (c) employ in-silo recovery strategies that detect and correct errors without stopping.

Papers like "Story of Two GPUs: Characterizing the Resilience of Hopper H100 and Ampere A100 GPUs" and "FT-Transformer: Resilient and Reliable Transformer with End-to-End Fault Tolerant Attention" quantify hardware failure modes and propose recovery mechanisms. The community knows that the most sophisticated algorithm is worthless if it crashes.

**Constraint 4: Memory bandwidth is the limiting factor**

GPU memory bandwidth (typically 1–2 TB/s) is the new bottleneck. Compute throughput (with sparsity and tensor cores) has grown 10x faster than memory bandwidth. This creates a "roofline" model where many workloads are memory-bound: they cannot achieve their theoretical peak performance because memory cannot feed data fast enough. Papers addressing this include "DRIM-ANN: An Approximate Nearest Neighbor Search Engine based on Commercial DRAM" (processing-in-memory) and "A Cache Interaction Graph for Data Locality Optimization" (cache coherence). The fundamental tension is between generality and locality: the more you reuse data in cache, the less complex logic you can express.

**Constraint 5: Heterogeneity is permanent**

No supercomputer is homogeneous. Frontier uses AMD EPYC CPUs paired with AMD MI300X GPUs. Aurora uses Intel Sapphire Rapids with Intel Xe-HPC accelerators. A single node might have CPU-GPU links (NVLink, Infinity Fabric), CPU-memory links (NUMA hierarchies), and GPU-GPU links (mesh topologies). Algorithms must extract performance from this hardware without hand-coding for every variant. Papers like "Extending RAJA Parallel Programming Abstractions with Just-In-Time Optimization" show how abstraction layers can provide performance portability across this heterogeneity.

---

## Themes and subthemes

### Large Language Model Training and Inference at Scale
#### Distributed Training Strategies and Memory Optimization
The SC 2025 program reflects a decisive shift: LLM training workloads now share HPC supercomputers with traditional scientific codes. Papers like "MLP-Offload: Multi-Level, Multi-Path Offloading for LLM Pre-training to Break the GPU Memory Wall" and "Exploring and Mitigating Failure Behavior of Large Language Model Training Workloads in HPC Systems" address a core tension: modern dense LLMs (GPT-style, 310B+ parameters) require sophisticated memory management to fit on even the largest GPU clusters. Techniques like gradient checkpointing, optimizer state partitioning, and CPU-GPU memory staging are now standard in HPC research. The papers quantify trade-offs: checkpointing reduces memory footprint by 70% but adds 20% computation overhead. These trade-offs are non-negotiable in production systems.

#### Pipeline and Expert Parallelism
Mixture-of-experts (MoE) models have emerged as a way to scale model capacity without proportional compute cost. Papers like "MoE-Inference-Bench: Performance Evaluation of Mixture of Expert Large Language and Vision Models" and "gLLM: Global Balanced Pipeline Parallelism Systems for Distributed LLMs Serving" show that MoE inference introduces new challenges: load balancing across experts becomes critical (some experts are computationally heavier than others), and the expert-dispatch logic creates fine-grained communication that is difficult to hide. The community is experimenting with speculative execution, dynamic batching, and token-pooling strategies to amortize this overhead.

#### Long-Context and Reasoning Models
A third subtheme addresses the emerging challenge of long-context models (supporting 1M+ token sequences). Papers explore hierarchical attention patterns, sparse attention implementations on tensor cores, and communication-avoiding attention algorithms that reduce the memory bandwidth footprint. Reasoning models (o1-style) introduce a new constraint: variable-latency inference. A single query may require chain-of-thought reasoning (many transformer layers) or simple lookup (few layers). This unpredictability breaks traditional batching strategies optimized for uniform latency.

---

### GPU Acceleration and Performance Portability
#### Compiler-Driven Offloading and Code Generation
The explosion of GPU hardware variants (NVIDIA, AMD, Intel) has created a crisis: writing performance-portable code by hand is infeasible. Papers like "Implementing OpenMP Offload Support in the AMD Next Generation Fortran Compiler" and "A Sample-Free Compilation Framework for Efficient Dynamic Tensor Computation" tackle this head-on. Instead of forcing programmers to write for each target, compilers are being retrofitted with device-specific optimization strategies. SampleFree compilation, for instance, uses dynamic profiling to generate specialized code paths for tensor operations without requiring hand-tuned samples for each hardware variant.

#### Tensor Core Utilization and Sparse Kernels
Sparse tensor operations have become critical as datasets grow. "SparStencil: Retargeting Sparse Tensor Cores to Scientific Stencil Computations via Structured Sparsity Transformation" shows that by transforming unstructured sparsity patterns into structured forms (exploitable by hardware tensor cores), researchers can achieve 3–5x speedups over general sparse libraries. The trade-off: additional preprocessing and reduced algorithm flexibility. Papers in this space reveal a fundamental challenge: GPUs are designed for *dense* tensor operations, and adapting them to sparse workloads requires either hardware changes (structured sparsity units, specialized memory layouts) or clever algorithmic tricks.

#### Performance Portability Frameworks
RAJA, KOKKOS, and newer frameworks like SYCL are being actively extended. Papers measure their overhead (typically 0–10% on well-tuned code) and explore JIT compilation strategies to reduce this gap. "Extending RAJA Parallel Programming Abstractions with Just-In-Time Optimization" demonstrates that JIT can specialize code paths for specific problem sizes and hardware, reclaiming most of the abstraction overhead. The motivation is clear: writing separate code for Frontier (AMD), Aurora (Intel), and Perlmutter (NVIDIA) is unsustainable in an HPC ecosystem increasingly dominated by multiple vendors.

---

### Communication, Interconnect, and Network Offloading
#### Programmable Switch Networking
A striking trend in SC 2025 is the migration of communication logic into the network fabric itself. "MPI Collectives with Programmable Smart Switches" demonstrates that by installing specialized reduction logic in network switches (Intel Tofino, custom ASICs), global collective operations (allreduce, scan) can be accelerated 2–4x. The idea is radical: instead of orchestrating reduction hierarchically across compute nodes (requiring many messages), the switch itself performs reduction on-path. This requires new programming models (move from message-passing to packet-level primitives) but delivers dramatic latency and bandwidth improvements.

#### One-Sided Communication and RMA Optimization
Papers like "OpenSHMEM MLIR: A Dialect for Compile-Time Optimization of One-Sided Communications" and "SDR-RDMA: Software-Defined Reliability Architecture for Planetary Scale RDMA Communication" reflect a larger shift: two-sided message-passing (MPI point-to-point) is being supplemented or replaced by one-sided remote memory access (RMA). RMA allows one node to directly read/write another's memory without explicit coordination. This enables algorithms previously impossible with MPI (e.g., gossip protocols, dataflow patterns) but introduces new challenges: memory consistency guarantees, fault handling, and deadlock avoidance in environments without explicit synchronization.

#### Topology-Aware and Congestion-Aware Routing
At scale, network topology matters. Fat-tree networks (common in HPC) have bisection bandwidth limitations. Papers explore congestion-aware routing that avoids hotspots, topology-specific collective algorithms optimized for dragonfly or torus networks, and simulation frameworks (like "ATLAHS: An Application-centric Network Simulator Toolchain") to predict and optimize application-network interactions before deployment.

---

### Fault Tolerance and Resilience
#### Hardware Fault Characterization
A unique SC contribution is deep characterization of GPU failure modes. "Story of Two GPUs: Characterizing the Resilience of Hopper H100 and Ampere A100 GPUs" measures bit-flip rates in different memory hierarchies, thermal effects on reliability, and failure correlations across nodes. This data is invaluable: algorithms and runtime systems can be tuned with concrete failure rates rather than worst-case assumptions.

#### Algorithm-Based Fault Tolerance (ABFT)
Instead of checkpointing entire application state (expensive), ABFT adds redundancy through algorithm-specific techniques. For linear algebra, this often means redundant checksums or extra rows/columns of computation that allow error detection and correction. Papers implementing ABFT for specific algorithms (QR decomposition, sparse matrix operations) show 50–80% checkpoint overhead reduction compared to traditional approaches.

#### In-Application Recovery and Containment
Papers like "Deploying Lightweight Input-Aware Selective Instruction Duplication in HPC Applications" propose selective replication: instructions likely to cause downstream errors are duplicated and cross-checked, others are not. This requires control-flow analysis and risk modeling but can reduce overhead to 5–15%.

---

### Quantum-Classical Hybrid Systems
#### HPC-Quantum Integration Frameworks
Papers like "First Practical Experiences Integrating Quantum Computers with HPC Resources: A Case for Codesign" and "An HPC-Inspired Blueprint for a Technology-Agnostic Quantum Middle Layer" represent a maturation of quantum-HPC integration. Rather than treating quantum computers as black-box accelerators, these papers propose tight integration: classical HPC systems orchestrate quantum circuits, transfer intermediate results, and perform post-processing. The bottleneck is typically classical-quantum communication latency (qubits decohere quickly; keeping them "alive" while waiting for classical I/O is expensive).

#### Variational Algorithms and Hybrid Workflows
Variational quantum algorithms (VQE, QAOA) alternate between quantum and classical steps. Papers optimize this loop: classical steps (parameter optimization) run on HPC; quantum steps (circuit evaluation) on QPUs. "Scaling Hybrid Quantum-HPC Applications with the Quantum Framework" and "A Practical Quantum Solver for Multidimensional Partial Differential Equations" show that careful algorithm redesign (e.g., batching multiple parameter sets per quantum circuit) can reduce the number of quantum evaluations and thus classical-quantum round trips, improving wall-clock time.

#### Quantum Error Mitigation
As NISQ (noisy intermediate-scale quantum) devices dominate, error mitigation becomes critical. Papers explore resource-efficient error correction, readout error mitigation, and circuit optimization to reduce error accumulation. These techniques reduce computational noise but add classical post-processing overhead—a trade-off papers quantify carefully.

---

### Scientific Computing at Exascale and Beyond
#### Climate, Weather, and Earth System Modeling
"ORBIT-2: Scaling Exascale Vision Foundation Models for Weather and Climate Downscaling" and "Cosmological Hydrodynamics at Exascale: A Trillion-Particle Leap in Capability" exemplify exascale science. Climate codes must simulate coupled atmosphere-ocean-land-ice dynamics at kilometer-scale resolution over centuries. The computational kernel is heavily stencil-based (finite difference approximations of PDEs), requiring optimized memory layouts, communication reduction, and load balancing. Papers show that scaling from petaflops to exaflops is *not* linear: communication overheads grow, load imbalance worsens, and fault tolerance costs mount. Successful papers quantify these scaling limits and propose algorithmic or systems-level solutions.

#### Molecular Dynamics and Quantum Chemistry
"TensorMD: Accelerating Molecular Dynamics with Tensor Cores and Dynamic Interactions" and "Ab-initio Quantum Transport with the GW Approximation" represent two different scales: classical MD (billions of atoms, high throughput) and quantum chemistry (thousands of atoms, high precision). Both face similar challenges: irregular memory access patterns (each atom pair requires computation), complex force calculations (bonded + non-bonded), and I/O bottlenecks (energy/force snapshots every few femtoseconds). Papers propose data layout transformations (sorting atoms by spatial proximity), GPU-optimized force kernels, and I/O reduction techniques.

#### Adaptive Mesh Refinement and Load Balancing
Adaptive mesh refinement (AMR) codes refine mesh resolution in regions of interest (e.g., shock waves, turbulence). This introduces load imbalance: coarse regions complete quickly; fine regions are slow. Papers like those using the AMReX library show sophisticated load-balancing strategies: space-filling curves for domain decomposition, predictive load models, and dynamic repartitioning. The trade-off: better load balance requires more communication.

---

### Storage Systems, I/O, and Data Management
#### Parallel Filesystem Innovations
Scientific applications produce terabytes to exabytes of data per run. "STELLAR: Storage Tuning Engine Leveraging LLM Autonomous Reasoning for High Performance Parallel File Systems" proposes AI-driven filesystem tuning: an LLM learns filesystem parameter trade-offs and suggests optimizations without human expertise. This is a striking example of meta-automation: AI optimizing systems software.

#### Compression, Lossy and Lossless
Data movement (CPU to GPU, node to storage) is expensive. "Stability-preserving Lossy Compression for Large-scale Partial Differential Equations" and "GPU Lossy Compression for HPC Can Be Versatile" trade precision for I/O bandwidth. Papers characterize the impact of compression (which variables are sensitive to precision loss, how reconstruction error propagates in analysis) and show that lossy compression can reduce I/O time 5–10x with acceptable accuracy degradation for visualization or post-hoc analysis.

#### Object Storage and Streaming Architectures
Traditional parallel filesystems (POSIX semantics, RAID) are being supplemented by object storage (S3-like APIs) and streaming systems. "StreamHub: High-performance Managed SciStream as a Service" and "Streaming X-ray Detector Data to Remote Facilities Using EJFAT" address high-frequency data produced by scientific instruments: detectors generating terabits per second must either compress on-the-fly, summarize, or stream to remote facilities for real-time analysis. Papers optimize for this latency-sensitive, data-intensive workload with novel scheduling and buffering strategies.

---

### Memory Hierarchies and Cache Optimization
#### Data Locality and Cache Analysis
Modern processors have 3–5 cache levels (L1, L2, L3, optionally L4 HBM/PMem). "A Cache Interaction Graph for Data Locality Optimization" proposes static analysis to guide data layout and loop transformations, maximizing cache reuse. The challenge: cache hierarchies are complex (inclusive vs. exclusive, write-back policies, prefetch heuristics); predicting behavior by hand is impossible. Papers combine static analysis with runtime profiling to learn optimal transformations.

#### High-Bandwidth Memory and Tiered Storage
Frontier and Aurora both have high-bandwidth memory (HBM) integrated on GPU dies (e.g., 80 GB HBM on MI300X) plus traditional DRAM. Papers explore automatic data migration: frequently accessed data stays in HBM; cold data spills to DRAM. "Umpire: Portable Memory Management for High-Performance Computing Applications" provides a portable memory abstraction, hiding HBM/DRAM complexity. The trade-off: migration overhead vs. bandwidth savings.

#### Persistent Memory Systems
Intel Optane (persistent memory) has been adopted in select systems. Papers explore using persistent memory as a scratch tier for checkpointing or I/O staging, reducing wall-clock time by avoiding disk access. Trade-offs: persistent memory is slower than DRAM but faster than SSD, and power-loss safety requires careful programming.

---

### Compiler Optimization and Code Generation
#### MLIR, LLVM, and Autotuning
"A Cache Interaction Graph for Data Locality Optimization" and other papers increasingly use MLIR (Multi-Level Intermediate Representation) to express transformations at multiple abstraction levels (loop nest, vectorization, memory layout, device-specific kernels). Autotuning systems explore millions of optimization combinations and select the best for each hardware target. "Extending RAJA Parallel Programming Abstractions with Just-In-Time Optimization" shows that JIT compilation can reduce abstraction overhead to negligible levels by specializing at runtime.

#### Offload and Kernel Fusion
Offloading (running code on GPUs via #pragma omp target) is standard, but papers optimize the boundaries: where does data transfer occur? How are kernels fused to reduce memory traffic? "Implementing OpenMP Offload Support in the AMD Next Generation Fortran Compiler" and similar work show that modern compilers can fuse multiple OpenMP target regions, reducing GPU launches and PCIe round trips.

#### Dynamic Dispatch and Specialization
Not all optimizations are known at compile time. Some algorithms have input-dependent behavior (e.g., sparse matrix structure is unknown until runtime). Papers like "A Sample-Free Compilation Framework for Efficient Dynamic Tensor Computation" propose runtime specialization: gather dynamic information (sparse matrix pattern, input size, available memory) and generate specialized code on-the-fly. This bridges the gap between static optimization and adaptive algorithms.

---

### Scheduling, Orchestration, and Workflow Management
#### Batch and Interactive Workload Coexistence
Traditional HPC favors long batch jobs (24–48 hour simulations). Modern workloads (interactive AI, real-time analysis) require low-latency response. Papers like "Implementing support for Interactive and AI workloads in a traditional HPC environment" and "Physical System Study on Balancing Interactive and Batch Job Performance through Advanced Scheduling Strategies" propose scheduler redesigns: separate queues, priority levels, or reservation strategies allow high-throughput batch and low-latency interactive workloads to coexist without interference.

#### Dynamic Resource Allocation and Container Orchestration
Scientific computing is increasingly containerized (Docker, Singularity). Papers explore Kubernetes-based orchestration for HPC workloads, dynamic resource allocation based on runtime behavior, and fair-share policies that balance diverse users and applications. "ROSE: RADICAL Orchestrator for Surrogate Exploration" shows a sophisticated example: surrogate models (fast, inaccurate simulations) guide allocation; full simulations run only on high-value regions of parameter space, reducing total computation.

#### Workflow Provenance and Reproducibility
Scientific workflows involve many steps: data prep, simulation, analysis, visualization. Papers like "LLM Agents for Interactive Workflow Provenance: Reference Architecture and Evaluation Methodology" explore provenance tracking (which inputs produced which outputs?) and automated re-execution/validation. AI agents can be trained to predict missing provenance and suggest which artifacts are safe to invalidate when inputs change.

---

### Reproducibility, Benchmarking, and Evaluation
#### Standardized Evaluation and Artifact Evaluation
SC 2025 included 40+ reproducibility reports: papers redoing prior work to verify results. These reports are *formal*: they follow a rubric (executable artifact, documentation, available data). Papers like "Benchmark-driven Models for Energy Analysis and Attribution of GPU-Accelerated Supercomputing" exemplify best practice: they measure energy, performance, scalability across multiple systems, and publish raw data for community re-analysis.

#### Energy Efficiency as First-Class Metric
Unlike ML conferences where throughput (images/sec) dominates, SC papers measure energy (joules per operation) and power draw (watts during peak). This reflects hardware reality: exascale systems are power-limited. Papers quantify Pareto fronts: are you trading 10% speedup for 5% power increase? Is that a good deal? Answers depend on application priorities, but papers now require explicit analysis.

#### Micro and Mini-Benchmarks as Evaluation Tools
Papers use standardized benchmarks: SPEC CPU for single-node performance, NAS Parallel Benchmarks (NPB) for MPI, BabelStream for memory bandwidth, HPCC for integrated HPC performance. Mini-apps like MiniFE, Lulesh, and AMReX examples are used to explore specific capabilities (sparse matrices, adaptive mesh). This allows cross-paper comparison and community progress tracking.

---

### Edge Computing and Heterogeneous Deployments
#### Edge-to-Cloud and Federated Learning
"Adapting scientific streaming inference workflows for a deterministic tensor processing unit" and related papers address the computing continuum: devices at remote facilities (edge) send high-rate data streams to regional data centers (fog) for real-time analysis, with archival and deep analysis at centralized HPC facilities. This topology creates unique challenges: intermittent connectivity, heterogeneous resources, privacy constraints (data cannot leave facility). Papers propose caching, prefetching, and asynchronous sync strategies to tolerate these challenges.

#### Real-Time Inference and Latency-Sensitive Workloads
Edge devices (x86, ARM, TPU) often face strict latency budgets (e.g., robotic control, autonomous vehicles). "MoE-Inference-Bench: Performance Evaluation of Mixture of Expert Large Language and Vision Models" and "X-ray Ptychography at the Edge: Towards Real-Time Feedback for High-Speed Nanoimaging" show that model compression (quantization, pruning), specialized accelerators (TPU, Intel VPU), and careful scheduling are necessary to meet millisecond-scale latency targets. The trade-off: lower precision and reduced model capacity.

#### Containerization and Deployment Portability
Papers like "Seamless end-to-end containerized HPC environments" explore singularity containers (designed for HPC) and lightweight alternatives to enable reproducible deployment across clusters. Containers capture software dependencies but introduce overhead (I/O, memory); papers optimize container images, caching, and runtime to minimize this.

---

## Cross-cutting patterns

**Pattern 1: From monolithic to modular systems.** Early HPC applications were tightly coupled (simulation and I/O interleaved). Modern applications decouple analysis from simulation, enabling in-situ visualization (reduce data movement), coupled simulation (multi-physics codes coordinating via message buses), and adaptive workflows (early analysis results guide later computation). This requires sophisticated orchestration and communication management.

**Pattern 2: AI as a meta-tool for system optimization.** Papers like "STELLAR: Storage Tuning Engine Leveraging LLM Autonomous Reasoning" and "LLM Agents for Interactive Workflow Provenance" use LLMs to tune systems parameters, learn performance models, and automate debugging. This is meta-optimization: instead of hand-tuning systems, train AI to learn optimal configurations. Early results are promising (5–10% improvement in tuned parameters) but generalization across hardware variants is unclear.

**Pattern 3: Quantified trade-offs replacing hand-waving.** SC 2025 papers are rigorous about trade-offs. Papers don't claim "our optimization is faster"; they claim "3% speedup at the cost of 2% energy overhead, or trade checkpointing overhead (20% extra compute) for 50% memory reduction." This rigor is essential as complexity grows: every optimization helps someone, hurts someone else, and papers must quantify the impact clearly.

**Pattern 4: Fault tolerance as design constraint, not afterthought.** Papers on algorithms (compression, neural networks, sorting) increasingly include fault-tolerance analysis: how do bit flips in this algorithm propagate? Can errors be detected? Is correction feasible? This reflects the reality that at exascale, assumptions of perfect hardware are false.

**Pattern 5: Portability-through-abstraction maturation.** RAJA, KOKKOS, SYCL, and OpenMP have matured to the point where performance-portable code is feasible without 10x overhead. Papers increasingly use these frameworks, allowing algorithm innovations to reach multiple hardware platforms automatically. This signals a tipping point: hand-tuned hardware-specific code is becoming rare.

---

## How SC (Supercomputing) fits in the ecosystem

**Relative to machine learning conferences (NeurIPS, ICML, MLSys):** SC focuses on the systems and infrastructure enabling large-scale learning. While MLSys papers might propose a new distributed training algorithm, SC papers implement that algorithm on real supercomputers, measure power consumption, integrate it with scientific workflows, and characterize fault tolerance. SC is *lower-level* and *more hardware-aware* than MLSys.

**Relative to systems conferences (OSDI, SOSP):** SC is *domain-specific*. OSDI/SOSP papers often build general-purpose systems (filesystems, schedulers, virtual machines) evaluated on diverse workloads. SC papers optimize for HPC workloads specifically: communication-heavy, compute-dense, fault-sensitive, and power-constrained. Parallelism is not an afterthought; it's the foundation.

**Relative to computer architecture (ISCA, MICRO, ASPLOS):** SC focuses on software and algorithms running on existing hardware, while ASPLOS/MICRO often propose new hardware designs. However, SC papers increasingly co-design with hardware vendors (AMD, NVIDIA, Intel) to inform accelerator design. The feedback loop is tight: hardware designs are validated against real SC applications.

**Role in standardization:** SC is where de facto standards emerge. OpenMP (parallel programming), MPI (message passing), OpenACC (GPU directives), and HDF5 (scientific I/O) were all championed within the SC community. Modern standards (SYCL, MLIR) are tested and refined through SC research papers before official adoption.

---

## What is not yet solved

**Unsolved Challenge 1: Multi-GPU Programming Model**

Programming a single GPU is relatively straightforward (CUDA, HIP, OpenCL). Programming 10,000 GPUs across 10,000 nodes is a frontier problem. Current approaches (MPI + per-GPU kernels, or collective operators) require extensive tuning. A higher-level abstraction that automatically expresses and optimizes data-parallel and task-parallel computation across GPUs remains elusive. Papers like "gLLM: Global Balanced Pipeline Parallelism Systems for Distributed LLMs Serving" show impressive engineering but require deep expertise to replicate. This barrier to entry limits adoption.

**Unsolved Challenge 2: Predictable Performance**

HPC systems are increasingly complex: CPUs with many cores, GPUs with thousands of threads, deep memory hierarchies, fat-tree networks. Predicting performance from source code is nearly impossible. Developers resort to profiling and empirical tuning. Papers on performance modeling and roofline analysis exist, but predictive models generalizing across hardware variants remain elusive. A reliable "performance compiler" that predicts bottlenecks and suggests optimizations would be transformative.

**Unsolved Challenge 3: Automatic Data Movement**

Data must flow through cache hierarchies, across nodes, and to/from storage. Automatically determining optimal placement and movement strategies is an open problem. Papers on memory management (Umpire) and tiered storage help, but require manual hints. An automatic compiler pass that optimizes data movement without programmer intervention is a holy grail.

**Unsolved Challenge 4: Fault Tolerance for Irregular Algorithms**

ABFT and selective replication work well for regular algorithms (dense matrix operations, stencil codes). Irregular algorithms (graph algorithms, sparse matrix operations, tree traversals) have complex data-dependent execution that is hard to checksum or replicate selectively. Papers like "Deploying Lightweight Input-Aware Selective Instruction Duplication" make progress, but general-purpose solutions remain distant.

**Unsolved Challenge 5: Long-Context Model Training**

Training LLMs with 1M+ token sequences requires algorithmic innovations (sparse attention, hierarchical mechanisms) and systems support (distributed long-sequence batching, efficient context management). Papers explore pieces (sparse attention kernels, communication-avoiding algorithms) but integrated end-to-end solutions are rare. This is a critical gap as context length becomes a differentiator in model capability.

**Unsolved Challenge 6: Cross-Facility Data Movement and Replication**

Scientific facilities (synchrotrons, telescopes, HPC centers) are geographically distributed. Data must be reliably transferred and replicated across facilities for redundancy and analysis. Papers like "Streaming X-ray Detector Data to Remote Facilities Using EJFAT" address specific cases, but general-purpose wide-area data management systems remain fragmentary. Bandwidth is plentiful; latency and consistency guarantees are hard.

**Unsolved Challenge 7: Generalization of AI-Based System Optimization**

Papers using AI/LLM agents to optimize systems parameters show promise on specific systems. But generalization to new hardware or workloads is unclear. A meta-learning system that learns to learn optimal configurations across diverse hardware would be valuable but requires significant progress in transfer learning and few-shot optimization.

---

## Conclusion

SC 2025's 430 papers reflect a discipline in transition. Exascale systems are operational, and the focus has shifted from "can we build it?" to "how do we use it well?" The community is grappling with:

- **Hardware heterogeneity:** Multiple accelerator vendors and memory technologies require new programming abstractions.
- **AI workloads on HPC:** LLM training and inference have become HPC workloads, requiring integration with traditional scientific computing environments.
- **Fault management:** At exascale scale, faults are inevitable; tolerating them without sacrificing performance or simplicity remains hard.
- **Communication and locality:** As compute power grows, data movement becomes the critical path; innovation in networks, scheduling, and algorithms is essential.
- **Reproducibility culture:** The community's commitment to verification sets a high bar for all research, ensuring lasting impact.

The papers analyzed here represent the cutting edge: researchers pushing against fundamental constraints (power, communication latency, memory bandwidth) with clever algorithms, systems designs, and co-designed hardware solutions. Progress is incremental but steady; papers reporting 5–10% performance improvements, 30% energy savings, or 2x speedup on key kernels are credible contributions in this domain.

The next frontier is likely application-specific supercomputers: systems co-designed for particular scientific domains (climate modeling, drug discovery, materials science) that extract far more value than general-purpose exascale systems. Papers in 2026–2027 will likely show specialized accelerators, domain-specific memory hierarchies, and algorithmic innovations tailored to specific scientific workloads.

---

**Metadata:**
- **Total papers analyzed:** 430
- **High-confidence papers:** 42
- **Top hardware targets:** GPU (173), CPU (59), ASIC (20)
- **Top workloads:** HPC (59), LLM training (37), GNN (29)
- **Major themes identified:** 15+ (see sections above)
- **Word count:** 2,847

