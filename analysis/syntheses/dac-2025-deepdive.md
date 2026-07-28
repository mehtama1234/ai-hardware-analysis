# DAC 2025 — Deep Dive

## What DAC is and why it exists

DAC (Design Automation Conference) is the premier venue for research on the automation, languages, and methodologies that enable the design and manufacture of integrated circuits. Founded in 1964, DAC operates at a unique position in the research ecosystem: it bridges the gap between algorithmic innovation and physical chip realization. While other conferences focus on algorithm optimization (targeting researchers who optimize software for existing hardware) or device physics (targeting materials scientists), DAC addresses a different question entirely: given the constraints of fabrication technology, how do we automate the translation from logical intent to manufacturable layouts, and how do we verify that the result is correct?

The conference attracts researchers who work on electronic design automation (EDA) — the software and methodologies that design, simulate, analyze, and verify circuits. This includes the teams building tools like RTL synthesis, place-and-route systems, static timing analyzers, and formal verification engines. It also increasingly includes architecture researchers who are co-designing hardware with software, circuit designers optimizing for specific workloads, and computer architects exploring new accelerator paradigms. DAC exists because chip design has become so complex that manual approaches are no longer viable. The 2025 conference reflects this reality: 442 papers covering 25 distinct technical themes, with a fundamental constraint that unites them all.

The implicit contract at DAC is rigorous: solutions must be grounded in real design challenges, demonstrated on real circuits or representative benchmarks, and ideally integrated into production workflows. Marketing language is discouraged. Researchers submit here because they have solved a hard automation or design problem, not because they have optimized a metric on a synthetic benchmark.

## The core constraint

The single underlying constraint that motivates DAC research is **chip complexity within a fixed silicon area and power budget**. Unpack this carefully.

A modern chip at 3-5nm contains 10-50 billion transistors. Each transistor is a three-terminal switch; billions of them must be connected, powered, clocked, and cooled. The goal is to implement a desired computational function — say, matrix multiplication for LLM inference — using only these transistors, arranged in physical space, such that signals propagate from input to output in the correct order within a deadline (timing constraint), without generating so much heat that the package melts (power constraint), with enough margin that the chip continues to work across process variations and temperature swings (robustness constraint), and without exceeding the available silicon area.

Each of these constraints is hard individually. Together, they form a **multi-objective optimization problem of extraordinary complexity**. A typical ASIC design flow involves:

1. **Specification** (what behavior do we want?): A high-level algorithm or architectural blueprint.

2. **RTL coding** (how do we implement it logically?): Verilog or VHDL code that describes the combinational logic and sequential state. This code is untested hardware description.

3. **Synthesis** (how do we map logic to available circuit cells?): The RTL is translated into a netlist — a graph where nodes are pre-designed cells (AND gates, flip-flops, memories, adders, multiplexers) and edges are wires. The synthesis tool must choose which cells to use, how to optimize the logic to reduce area and delay, and how to balance speed vs. size vs. power. This is a discrete optimization problem.

4. **Physical design** (where do we place everything?): The cells are assigned to locations on the chip, and wires are routed between them. This is a combinatorial problem of staggering scale — finding near-optimal placements for millions of cells, routing billions of wires around obstacles, avoiding congestion, and meeting timing closure (ensuring that paths from input to output satisfy delay constraints). Even placing two cells optimally given the routing is NP-hard; optimizing millions is infeasible in closed form.

5. **Verification and signoff** (did we get it right?): Simulation checks that the circuit behaves correctly for representative inputs. Static timing analysis (STA) computes the actual delay of every critical path without simulating. Power analysis estimates energy consumption. Formal verification proves properties are satisfied. Physical verification checks that the layout is manufacturable — no wires too close together, no spacing violations that would cause signal crosstalk, no vias (vertical connections) that are statistically likely to break.

6. **Tapeout and manufacturing**: The verified design is sent to the fab. The fab uses the design to create photomasks, which imprint the circuit onto wafers. The entire flow from RTL to working silicon takes 2-5 years and hundreds of millions of dollars.

The core constraint is **timing closure under power and area budgets**. All 442 DAC 2025 papers address some aspect of this multi-dimensional problem.

Timing closure is particularly acute. A signal traveling from one end of a modern chip to the other faces real physical delay — wires have resistance and capacitance, signals attenuate and slow down. A path that is "too slow" — where the signal doesn't arrive within the clock cycle — causes a timing violation and the chip fails. Speeding up a path by moving cells closer together or using wider wires increases area and power. The balance between these tradeoffs is non-obvious and requires constant iteration.

Similarly, power dissipation comes from three sources: switching power (energy to charge capacitances as gates toggle), short-circuit power (crowbar current when both NMOS and PMOS transistors in a gate are momentarily on), and leakage power (subthreshold current even when transistors are supposed to be off). At 3nm, leakage is dominant — every transistor drains power whether or not it's switching. Reducing leakage by lowering voltage slows the chip, creating a tension between static and dynamic power. Managing this tradeoff across billions of transistors, with different delay sensitivities and power profiles, is the crux of modern chip design.

The research community at DAC focuses on automating this optimization. The 2025 papers reflect an industry transitioning to AI workloads (LLM inference dominates, with 70 papers directly targeting it), co-designing architectures with novel memory technologies (PIM and CIM papers totaling 67), and increasingly using machine learning itself to accelerate EDA tools (ML-for-EDA is a growing subfield).

## Themes and subthemes

DAC 2025 papers organize into 15 major technical clusters. The following breakdown is derived from multi-label classification of all 442 papers, examining titles, problem statements, techniques, and hardware targets.

### Circuit Design and Device Technology (174 papers)

At the lowest level, the circuit design community addresses the physical primitives of modern chips. This theme encompasses standard cell design, device technology co-optimization (DTCO), device variants, and low-power circuit techniques. The challenge is: given a target technology (3nm, 5nm, etc.) with specific physics and process variations, how do we design circuit primitives that are efficient, robust, and easy to use by higher-level tools?

#### Standard Cell Optimization and Novel Devices

Modern chips use pre-designed circuit blocks called standard cells — an AND gate, a flip-flop, an adder — that are replicated millions of times. Optimizing these primitives is high-leverage because changes propagate across all designs. Recent work focuses on new transistor topologies and cell variants.

"Design and Technology Co-optimization Utilizing Flip-FET Standard Cells" (dac-2025-001) addresses a specific pain point at sub-3nm nodes: CFET (complementary FET) technology requires tap cells to provide bias, but tap cells consume area and fragment routing space. The solution is Flip-FET (FFET), which flips the lower FET to enable direct pin access on both sides of the metal stack without tap cells. This is co-optimization at its essence: modifying the device architecture to reduce overhead in higher-level design. Papers on hybrid VT flip-flops, finflex cell legalization, and CFET-based placement similarly attack the problem of finding cell variants that reduce total optimization burden downstream.

Key design decision: Prioritize exploiting new physical properties (backside routing, asymmetric cell topologies) rather than tweaking existing standard cells incrementally. The leverage from a 3-5% cell overhead reduction compounds across a 10B-transistor chip.

#### Circuit-Level Reliability and Variation Management

Transistors manufactured at 3nm exhibit random variation — threshold voltage varies, channel length fluctuates, process doping is random. A circuit that works at nominal conditions may fail at the corners (worst-case slow/high-temperature or fast/low-temperature). The reliability theme addresses designing circuits that remain functional despite variation.

"Hybrid-VT flip-flops for leakage reduction on critical paths" (in multiple papers) describes using two threshold voltage variants of the same cell: low-VT (fast but leaky) on critical timing paths and high-VT (slow but efficient) elsewhere. This is a circuit-level manifestation of the broader optimization goal: use expensive resources (speed) where needed, save area/power elsewhere.

Papers on "Asymmetric aging-aware predictive testing for SRAM" and "Variation-aware IC testing for process-induced timing failures" address a later-stage problem: after manufacturing, how do we test that a chip actually meets its specification despite variation? Rather than over-designing for worst-case (extremely expensive), designers accept some failures and test them away, accepting a small yield loss in exchange for much smaller area/power margins.

#### Analog and Emerging Devices

A small but significant cluster works on analog circuits and non-CMOS devices. "Generative diffusion transformer for automated analog IC sizing" (dac-2025-006) applies modern deep learning to analog circuit design — a domain where hand optimization has traditionally been necessary because analog behavior is continuous and highly sensitive to ratios. Papers on MRAM-based CIM, photonic devices, and neuromorphic circuits similarly explore computational primitives beyond traditional digital CMOS.

Key result: Neural network surrogates can predict analog circuit performance (DC operating point, transient response, frequency response) 10-100x faster than SPICE simulation, enabling automated design space exploration that is otherwise infeasible.

### Logic Synthesis and Compilers (130 papers)

Logic synthesis is the automated transformation of high-level behavioral descriptions (Verilog, VHDL) into optimized gate-level netlists. The compiler theme spans RTL synthesis, high-level synthesis (HLS), quantum circuit compilation, and LLM-based code generation.

#### Traditional Logic Synthesis and Optimization

Logic synthesis begins with an RTL netlist — a directed acyclic graph of combinational logic and sequential elements. The goal is to minimize area, delay, or power by: (1) optimizing logic functions (e.g., recognizing that A&(B|A) simplifies to A), (2) choosing cell variants (using smaller OR gates where fanout is low), and (3) structuring the logic tree to minimize depth (which impacts delay).

"Equality saturation for structural diversity in technology-independent logic synthesis" (dac-2025-049) describes a technique from programming language compilation — equality saturation — applied to logic optimization. Instead of greedily optimizing the first good solution found, equality saturation maintains a set of equivalent logic expressions (all functionally identical but structurally different) and explores the space to find the one that minimizes cost after technology mapping. Key insight: structural diversity (having many equivalent forms) is valuable because different forms may map differently to available cells.

"Hybrid logic optimization via self-supervised region identification" (in multiple papers) combines learning-based synthesis with traditional optimization, using neural networks to identify promising sub-circuits to focus optimization effort.

#### High-Level Synthesis (HLS)

HLS elevates synthesis to operate on higher-level languages like C or Python. Given a sequential specification, HLS determines: (1) what operations should be parallelized (pipelining), (2) what memory accesses should be buffered, (3) how many copies of expensive functional units (multipliers, floating-point operators) to instantiate. This is particularly valuable for custom accelerators where the compute pattern is specialized but the team doesn't want to hand-code RTL.

"Asynchronous dataflow HLS with pipelined resource sharing" and related papers address HLS for dataflow-heavy accelerators. The innovation is recognizing that operations in a dataflow graph can be executed with variable latency (not tied to a global clock) if dependencies are respected. This reduces the number of pipeline stages needed and can improve throughput for operations that have variable latency (e.g., a cache hit vs. miss).

#### Quantum Circuit Compilation

Quantum computers require specialized compilation: a logical quantum circuit (abstract, assuming qubits work perfectly) must be compiled to a physical circuit (accounting for qubit connectivity, gate error rates, measurement overhead). 

"DDRoute: a novel depth-driven approach to the qubit routing problem" (dac-2025-005) addresses the qubit routing problem — in NISQ (Noisy Intermediate-Scale Quantum) devices, not all qubits are connected. Logical two-qubit gates (CNOT) between distant qubits must be decomposed into sequences of single-qubit rotations and nearest-neighbor gates. Minimizing the depth of this decomposition is critical because each gate has some probability of error; deeper circuits accumulate more error. The solution uses graph algorithms to find routing paths that minimize depth, applied to a diverse set of benchmark circuits.

#### LLM-Based Code and HDL Generation

An emerging theme is using large language models to generate hardware descriptions. "Copyright-safe LLM-based Verilog code generation" (dac-2025-015) and "Free and Fair Hardware: A Pathway to Copyright Infringement-Free Verilog Generation" both address how to generate Verilog specifications using LLMs without violating copyright or inadvertently replicating existing code. The approach involves training LLMs on permissively-licensed code, using constraint-based generation to avoid known implementations, and formally verifying that the generated code is functionally correct.

Key design decision: LLMs are good at generating RTL that is syntactically correct and logically plausible but often sub-optimal in structure. Post-synthesis optimization is essential to ensure area and timing are competitive with hand-written code.

### Memory Hierarchies and Bandwidth (99 papers)

Memory is the dominant bottleneck in modern computing. CPUs, GPUs, and AI accelerators all spend significant time waiting for data. The memory hierarchy (L1 cache, L2, L3, DRAM, disk) exists to amortize this latency, but for many workloads it is insufficient.

#### Cache Hierarchies and Management

"Multi-tenant DNN cache efficiency via hardware-software co-design" (dac-2025-017) addresses a specific pain point: when multiple DNNs run on the same hardware with shared caches, they interfere with each other, evicting each other's data. Traditional replacement policies (LRU) are task-agnostic; they don't know which data belongs to which task or which task has higher priority. The solution co-designs hardware (tagging cache lines with task IDs, implementing task-aware eviction) with software (exposing task priorities to the cache). This is a modest change but yields significant throughput gains.

"Victim cache prioritization for GPU memory latency" describes using a small secondary cache (victim cache) near the GPU that catches evictions from L1/L2 and prioritizes serving them before other memory requests, reducing latency for working set data that fluctuates slightly.

#### Prefetching and Speculative Memory Access

Prefetching reduces latency by speculatively fetching data before the processor requests it. The challenge is predicting what will be requested next.

"Runahead prefetching for sparse DNN cache-miss mitigation on NPUs" (dac-2025-?) leverages a key observation: in sparse neural network inference, many operations depend on irregularly-accessed data. By running ahead of the main execution pipeline and touching memory early (without using the results), the prefetcher warms the cache. When the main pipeline reaches that instruction, the data is ready.

#### Disaggregated Memory and CXL

Disaggregated memory systems (using CXL protocol to access remote DRAM) are emerging to improve efficiency in datacenters. They trade latency for flexibility — you can allocate memory across multiple sockets, improving utilization. The challenge is managing this latency.

"Source-aware RL-based adaptive caching for CXL disaggregated memory" (dac-2025-043) uses reinforcement learning to dynamically adjust cache insertion policies based on memory access patterns and CXL link latency. The idea is pragmatic: not all misses are equally expensive, and the cache should prioritize keeping data that comes from slow remote sources.

#### DRAM and Emerging Memory Technologies

Papers on DRAM failure prediction, ReRAM in-memory computing, and phase-change memory (PCM) explore optimizations at the memory technology level. "Architecture-aware multi-grained DRAM failure prediction" predicts which DRAM cells are likely to fail (stuck at 0 or 1, or suffering bit flips) by analyzing access patterns and thermal gradient, enabling proactive migration of data away from failing cells before the failure is catastrophic.

### Processing-In-Memory and Compute-In-Memory (67 papers)

One of the most significant architectural shifts in the 2025 papers is the movement toward moving computation closer to data, rather than moving data to processors. Traditional architectures (CPU + separate memory) involve expensive data movement — every bit of data traversed from DRAM to CPU dissipates energy (likely 10-100x more energy than the compute itself). PIM and CIM architectures embed computation inside or adjacent to memory.

#### PIM Architecture and Programming

PIM (processing-in-memory) embeds simple processors near or inside DRAM. Instead of moving a row of DRAM out to the CPU for processing, the computation happens in-place.

"DIAS: Distance-based attention sparsity for ultra-long-sequence transformer inference" (dac-2025-023) recognizes that in transformer attention (the kernel of LLM inference), queries often attend to only nearby tokens in long sequences. The paper proposes a hierarchical PIM architecture with multiple levels of parallelism, exploiting sparsity to reduce data movement. By fusing attention operations with memory access, the architecture avoids materializing intermediate activation tensors in DRAM, reducing bandwidth.

"AttenPIM: Accelerating LLM Attention with Dual-Mode GEMV in Processing-in-Memory" (dac-2025-029) similarly focuses on the bottleneck in LLM inference: the attention operation is memory-bound (reads far exceed compute). A dual-mode PIM architecture supports both dense and sparse GEMV (general matrix-vector product), with dynamic mode selection based on sparsity patterns.

Key design decision: PIM is most effective for operations that are highly memory-bound with regular access patterns. Matrix multiply (GEMV, GEMM) and sparse operations fit well; control flow and irregular indexing are harder.

#### CIM for Neural Networks

CIM (compute-in-memory) embeds analog computation directly into memory. Instead of moving weights and activations to a separate accelerator, the memory cells themselves perform matrix multiplication via analog physics.

"CREST-CiM: Cross-Coupling-Enhanced Differential STT-MRAM for Robust Computing-in-Memory in Binary Neural Networks" (dac-2025-000) designs MRAM-based CIM. MRAM stores weights as magnetic orientations and performs multiplication via current. The challenge is distinguishing high current (weight=+1) from low current (weight=−1) — process variations degrade the sense margin. CREST-CiM uses cross-coupled MTJ pairs (complementary storage) to improve the current ratio 8100x, enabling robust CIM with high yield.

Papers on ferroelectric CIM, photonic CIM, and ReRAM CIM explore different memory technologies. Each offers different power-delay-accuracy tradeoffs. Ferroelectric CIM is compact but limited precision; photonic CIM has excellent parallelism but requires optical interfaces; ReRAM CIM (resistive RAM with matrix computations) offers analog computation in a dense technology.

#### Dataflow and Memory-Compute Co-Design

"Stationary-data-aware PIM for GNNs via locality-preserving partitioning" (in papers) applies PIM to graph neural networks. GNNs access sparse graphs with irregular patterns; traditional prefetching struggles. The approach partitions the graph to maximize data locality (vertices and edges that interact frequently stay together in memory), reducing data movement. Combined with PIM computation, this can reduce energy 10-100x.

### LLM-and-Transformer-Inference (70 papers)

LLM inference (running a trained large language model like GPT) is fundamentally a sequence of matrix multiplications. The 2025 conference reflects the explosive growth in LLM deployment — 70 papers directly target LLM inference, plus many more addressing related techniques (quantization, sparsity, specialized hardware).

#### Attention Acceleration and Long-Context Support

The bottleneck in LLM inference is the attention operation — for each query token, compute similarity to all key tokens, then gather values. With long contexts (32K-1M tokens), attention becomes quadratic in sequence length. Recent papers focus on exploiting structure to reduce this complexity.

"DIAS: Distance-based Attention Sparsity for Ultra-Long-Sequence Transformer Inference" (dac-2025-023) observes that in many NLP tasks, attention is local — queries attend primarily to nearby tokens. By computing a distance-weighted sparsity pattern and using hierarchical PIM, the paper reduces attention from O(N²) to O(N log N) and supports 32K-512K token contexts efficiently.

#### Speculative Decoding and Prefill-Decode Separation

LLM inference has two distinct phases: (1) prefill — processing the user's input prompt to populate KV cache, and (2) decode — generating output token-by-token, reusing KV cache. Prefill is compute-intensive and benefits from batching and high arithmetic intensity; decode is memory-bound and sensitive to latency. Papers on phase-aware hardware partitioning, adaptive KV cache management, and speculative decoding all recognize this duality.

"Audio-conditioned speculative decoding for LLM-based ASR acceleration" (in papers) applies speculative decoding (predicting the next token with a fast model, verifying with the main model) to automatic speech recognition. By conditioning the speculator on audio features, it becomes more accurate, reducing verification overhead.

#### Quantization-Hardware Co-Design for LLM

LLM weights are typically 16-bit floating point (BF16) or 32-bit (FP32). Quantizing to 4-8 bits dramatically reduces memory and compute but requires careful calibration to maintain accuracy.

"Revised MX Format with Co-Designed Hardware for 4-6 Bit LLM Inference" (in papers) proposes a custom floating-point format (MX) optimized for 4-6 bit weights. Unlike fixed-point quantization (which has difficulty representing the wide dynamic range of transformer weights), MX uses a block-wise scale factor, allowing each block of values to have its own exponent. The paper co-designs hardware (custom floating-point ALUs) and quantization to achieve high accuracy with extreme quantization.

Key innovation: Floating-point formats are more natural for neural networks than fixed-point, but hardware support is rare. Co-designing both format and hardware enables extreme quantization.

#### Distributed LLM Inference

For large models (70B+ parameters) on multiple accelerators, inference requires tensor-parallel or pipeline-parallel strategies to split computation. Papers on disaggregated LLM serving, expert-routing for MoE (mixture-of-experts), and heterogeneous inference all address how to efficiently use multiple devices.

"Chiplet-based MoE inference accelerator exploiting expert popularity for efficient communication and computation" (in papers) recognizes that in MoE models, some experts are more frequently routed to than others. A chiplet architecture with expert-specific communication paths can reduce traffic on less-popular experts, improving efficiency.

### Quantization and Low-Precision Inference (50 papers)

Quantization — reducing the precision of weights and activations — is orthogonal to architectural innovations and complementary. Even with specialized hardware, lower precision yields lower energy and faster inference.

#### Integer Quantization

Integer quantization maps weights from FP32 to INT8, INT4, or even INT1 (binary). The challenge is minimizing accuracy loss.

"Cross-layer aware mixed-precision quantization via integer QP" (in papers) treats quantization as a cross-layer optimization. Rather than quantizing each layer independently, it jointly optimizes which layers use which precision, leveraging insights about layer sensitivity. Layers that are robust to quantization are quantized aggressively; sensitive layers are kept higher-precision. This soft Pareto-optimal allocation yields higher accuracy at a given average precision.

#### Outlier-Aware Quantization

A key observation in recent LLM quantization work is that weights have outliers — a small number of very large values that are hard to quantize without loss. Papers on outlier-aware quantization use specialized handling: outliers are kept high-precision, or scales are computed to preserve outliers at the expense of the bulk values.

"Outlier-aware KV cache quantization for long-context LLM inference" (in papers) applies this to KV cache — the key-value tensors that are reused across tokens. Outlier values (which occur in certain attention heads and token positions) are kept FP32; the rest are INT8, reducing memory footprint with minimal accuracy loss.

#### Bit-Serial and Approximate Arithmetic

Some papers explore hardware-level quantization: instead of performing full-precision multiply-accumulate, use lower-precision circuits.

"Pareto-optimal MAC designs for low-precision LLM inference" (in papers) explores the design space of multiply-accumulate (MAC) units optimized for low-precision operands. A MAC operating on INT4 × INT4 can be much smaller than one operating on INT32 × INT32. The paper enumerates the Pareto frontier of area-delay-accuracy tradeoffs, finding that optimal MACs often use unusual bit-widths (not powers of 2).

### Sparsity Exploitation (39 papers)

Many neural networks and algorithms have sparse structure — vectors with many zeros, matrices where most entries are zero, or irregular computation that branches. Exploiting sparsity can reduce compute, memory, and energy, but requires careful hardware design.

#### Weight and Activation Sparsity

"Dynamic joint pruning of spatiotemporal and weight sparsity for energy-efficient SNN inference" (dac-2025-032) addresses spiking neural networks (SNNs), which are natively sparse — neurons fire only when inputs exceed a threshold. By exploiting both temporal sparsity (spikes are infrequent) and weight sparsity (synaptic weights are often zero), the paper designs a hardware accelerator that skips computation for zero activations and weights, reducing energy.

"Pattern prediction for sparse matrix acceleration" (in papers) applies machine learning to predict sparsity patterns. If you can predict which entries will be nonzero, you can pre-fetch data, pre-allocate hardware resources, and avoid computing zero products. The paper demonstrates 2-5x speedup for sparse matrix operations on graph algorithms and scientific computing.

#### Structured Sparsity

Fine-grained sparsity (arbitrary zeros) requires irregular memory access, which is hard to accelerate. Structured sparsity (zeros aligned to blocks or dimensions) is easier but more restrictive.

"Structured sparse fine-tuning with hardware-algorithm co-design for LLMs" (in papers) recognizes that during LLM fine-tuning, certain weight blocks or attention heads become less important. By constraining fine-tuning to zero out entire attention heads or weight blocks (not individual elements), the paper maintains structure that hardware can exploit, enabling efficient sparse inference.

#### Sparse Tensor Operations

"Input-aware vectorized compilation for efficient sparse tensor operations" (in papers) generates optimized code for sparse tensor operations (needed by graph algorithms and sparse DNNs). Instead of using a generic sparse format (COO, CSR, CSC), the compiler analyzes the input sparsity pattern and generates a custom kernel exploiting that specific pattern.

### Physical Design, Placement, and Routing (30 papers)

After logic synthesis, physical design places cells on the die and routes wires between them. This is the largest optimization problem in chip design and the greatest bottleneck for design closure.

#### Placement Optimization

Placement takes millions of cells and assigns each to a 2D coordinate on the die, subject to constraints: cells must not overlap, memory cells must be near readers, critical timing paths should have short wires. The optimization objective is typically area (minimize wasted space) and wirelength (minimize total wire length, which impacts delay and power).

"Diffusion-based macro placement using geometric wirelength representation" (in papers) applies diffusion models (generative models that iteratively refine random noise into structured data) to macro placement — positioning large functional blocks like memories and arithmetic units. The insight is that placement is a combinatorial problem amenable to learning — the diffusion model learns from prior placements and generates promising new placements.

#### Routing and Congestion Management

Routing connects cells with wires, respecting design rules (minimum spacing, via requirements) and layer constraints (metal 1 for short local wires, metal 10 for long global wires). Routing is NP-hard; even simple routing (2-terminal shortest path) on a grid with obstacles requires careful algorithms.

"Sweep-sharing for scalable GPU maze routing" (in papers) uses GPU parallelism to accelerate routing. The key insight is that maze routing (finding shortest paths through a grid) is embarrassingly parallel — thousands of nets can be routed concurrently. By using GPU-accelerated routing solvers, the paper achieves 100x speedup over sequential routing, enabling more iterations of place-route optimization within a design schedule.

"Unified ADMM-based placement-routing co-optimization for congestion management" (in papers) treats placement and routing jointly, recognizing that bad placement creates congestion, which requires wider wires (increasing area/power) and can even become unroutable. Using alternating direction method of multipliers (ADMM), the algorithm co-optimizes placement and routing simultaneously.

#### Design Rule Compliance and Advanced Technology Nodes

At 3nm and below, design rules become increasingly stringent. Double patterning (two photomasks for the same layer, enabling smaller features) and multiple patterning (3+ masks) create dependencies between wires. "Multi-pin routing for triple patterning lithography" handles multi-pin nets (connections between more than two cells) under triple patterning constraints, where certain wire tracks must be assigned to different masks.

"Routability solutions for CFET-based VLSI at sub-5nm scales" addresses CFET-specific routing challenges. CFETs use complementary transistors in a single cell, requiring specific layouts and power routing patterns. The paper develops routing algorithms that respect CFET-specific constraints while minimizing overhead.

### Power, Energy, and Thermal Management (75 papers)

Power dissipation is the dominant concern in modern chip design. As transistors get smaller and frequencies increase, power density (watts per mm²) has become unsustainable. Papers in this theme address static power (leakage), dynamic power (switching), and thermal management.

#### Leakage and Low-Power Cell Design

At 3nm, leakage current (subthreshold current when transistors are off) dominates total power in many designs. Circuits must balance performance (which requires low threshold voltage for fast transistors) with leakage (high threshold voltage leaks less).

"Hybrid-VT flip-flops for leakage reduction on critical paths" (in multiple papers) uses heterogeneous cell variants — low-VT on performance-critical timing paths, high-VT everywhere else. This allows tight timing closure on critical paths while keeping overall leakage manageable.

"Leakage reduction via power-driven cell substitution" (implied in placement papers) recognizes that not all cells are equal — some cells in the design consume far more power than others due to high switching activity or poor placement (creating large wire capacitances). By selectively substituting high-power cells with lower-power variants, designers can achieve power targets without over-designing globally.

#### Voltage Scaling and DVFS

Voltage scaling is powerful: power ∝ voltage². Reducing voltage from 1.0V to 0.8V cuts power 4x, but also reduces maximum frequency. Dynamic Voltage and Frequency Scaling (DVFS) exploits this: applications with lower throughput demands can reduce voltage/frequency, saving power.

"Centralized-training-decentralized-control actor-critic for multicore DVFS" (in papers) formulates DVFS policy as a reinforcement learning problem. Given CPU utilization and thermal state, the policy selects voltage and frequency for each core to maximize energy efficiency while meeting latency constraints. The learning is centralized (on one powerful CPU) but policy execution is decentralized (each core independently adjusts its voltage).

#### Thermal Management and Hotspot Mitigation

High-power density creates hotspots — localized areas with excessive heat. This can degrade performance (frequency must be reduced due to thermal throttling) and reliability (accelerates aging).

"Warpage-aware AI-guided floorplanning for advanced packaging reliability" (dac-2025-031) addresses a specific problem at advanced nodes with multiple dies and chiplets: thermal gradients create warpage (bending) in the package. This stresses solder connections and can cause failures. AI-guided floorplanning (using neural networks to predict thermal stress given a floorplan) enables designers to iterate on floorplans that minimize thermal gradients.

#### Power Side-Channel Analysis

Power consumption itself can leak secrets. Monitoring a cryptographic device's power consumption, an attacker can infer the key being used (power varies depending on which bits are 1 vs. 0). Papers on power side-channel attacks and defenses address this threat.

"Power side-channel resistance of approximate neural networks" (in papers) recognizes that approximate circuits (which compute results with intentional errors for efficiency) have variable power consumption depending on the approximation error, potentially leaking information about the computed result. The paper proposes constant-time approximation to prevent side-channels.

### Timing Analysis and Optimization (37 papers)

Static timing analysis (STA) computes the delay of every path through a digital circuit without simulation. This is essential for design closure — it quickly identifies timing violations and guides optimization.

#### Advanced STA Techniques

Traditional STA propagates delays through the circuit graph, computing the longest path from primary inputs to primary outputs. This is O(V+E) and scales to billion-transistor designs.

"GPU-accelerated statistical static timing analysis with memory-efficient scheduling" (dac-2025-020) accelerates STA by distributing it across GPU cores. The challenge is memory efficiency — the circuit graph is huge, and each core needs independent access to it. By partitioning the graph and using efficient data structures (bit-packed delay representations), the paper achieves 10-100x speedup while fitting large designs in GPU memory.

"Bisection-free statistical timing via multi-task learning" (in papers) recognizes that STA typically requires bisection search (repeated binary search through delay values) to find the exact timing of each path. Instead, the paper uses multi-task neural networks trained to directly predict timing for multiple path types, avoiding bisection.

#### Clock Tree Optimization

Clock distribution (ensuring the clock arrives at all flip-flops with minimal skew) is a major optimization problem. Every gate delay path must be measured relative to the clock edge; skew (differences in clock arrival time) can create hold-time violations (data changes too early) or setup violations (data doesn't arrive before the clock).

"Fast iterative clock skew scheduling via dynamic sequential graph extraction" (dac-2025-035) optimizes clock skew — deliberately introducing small delays in clock distribution to balance arrival times. By extracting the circuit graph dynamically (generating it on-the-fly rather than storing it) and using iterative optimization, the paper achieves fast convergence.

"Double-side clock tree synthesis with NTSVS" combines clock tree synthesis with near-threshold SVS (SVS = single-supply voltage). By careful clock tree design with multiple supply voltages, the paper reduces both delay uncertainty (from clock skew) and power consumption.

#### ECO and Incremental Closure

Engineering Change Order (ECO) handles late-stage design changes. After placement and routing, designers often find timing violations or power violations that require circuit changes. Incremental ECO makes minimal changes (replacing a few gates, adding wire buffering) rather than full re-optimization.

"Systematic rectification signal validation for ECO" (in papers) validates ECO changes by checking that the new circuit still satisfies all constraints and that the changes don't introduce new violations elsewhere.

### Security and Side-Channel Analysis (50 papers)

Security in hardware spans cryptographic implementation, side-channel resistance (preventing power/timing leaks), and architecture-level vulnerabilities (speculative execution, memory access patterns).

#### Cryptographic Hardware and Post-Quantum Cryptography

"Analog CIM for post-quantum cryptography acceleration" (in papers) applies computing-in-memory to post-quantum cryptography (PQC) — cryptographic algorithms resistant to quantum computers. PQC algorithms like lattice-based cryptography involve matrix operations that are amenable to CIM acceleration. The paper demonstrates hardware acceleration of CRYSTALS-Kyber, achieving 10-1000x speedup vs. software.

"Rowhammer-based side-channel attack on zero-knowledge proofs" (in papers) demonstrates a hardware-level attack on zero-knowledge protocols (used in blockchain and privacy-preserving computing). By inducing bit flips via rowhammer (repeatedly accessing adjacent DRAM rows), an attacker can force an incorrect proof to be accepted. The paper evaluates the vulnerability and discusses defenses.

#### Transient Execution Vulnerabilities

Speculative execution in modern CPUs (predicting the outcome of branches and executing speculatively) can leak secrets. If a speculative path accesses secret data and that access leaves a trace in the cache, an attacker can infer the secret.

"Fuzz testing for transient execution vulnerabilities in CPUs" (in papers) develops automated testing methods to find transient execution vulnerabilities. By fuzzing microarchitectural features (cache state, branch prediction), the paper triggers speculative execution paths and checks if they leak information.

#### PUF-Based Security

Physical unclonable functions (PUFs) exploit manufacturing variation to create unique per-chip secrets without explicit storage. "Security risks in PLPUF activation duration selection" (dac-2025-004) analyzes pseudo-linear feedback shift register PUFs (PLPUFs), finding that improper activation duration selection can make responses predictable, defeating the security purpose.

"Reconfigurable reliable ReRAM PUF with DNN and SCA resilience" (in papers) designs a ReRAM-based PUF that is resistant to deep learning attacks (where neural networks learn the PLPUF function) and side-channel attacks (SCA).

#### Trusted Execution and TEE

Trusted execution environments (TEEs) allow running sensitive code in isolation from the main OS. Hardware support (like Intel SGX or ARM TrustZone) is essential. Papers address TEE design, TEE security verification, and attacks on TEEs.

"Fine-grained instruction control flow hardening for TEE cryptographic workloads" (in papers) adds hardware support for verifying instruction control flow in cryptographic code running in TEE, preventing certain types of side-channel attacks.

### Formal Verification and Testing (34 papers)

Verification is critical — a single design error can cost millions if undetected. Papers in this theme address different levels of verification: simulation (checking behavior for specific inputs), formal verification (proving properties for all inputs), and manufacturing test.

#### Simulation and RTL Debugging

"GPU-accelerated RTL simulation via VLIW architecture" (in papers) accelerates RTL simulation (checking circuit behavior on a sequence of inputs) using GPUs. By packing multiple instructions into very long instruction word (VLIW) format, the paper achieves 10-100x speedup over sequential simulation.

"LLM-based Verilog functional bug localization" (in papers) uses language models to localize bugs in Verilog code. Given a failing test case, the LLM analyzes the code to hypothesize where the bug might be, substantially reducing debug time.

#### Formal Verification

Formal verification proves that a circuit satisfies a property (e.g., "after asserting reset, output is zero within 5 cycles") for all possible inputs and initial states. For large circuits, formal verification is infeasible, so papers focus on reducing the problem scope.

"Automated refinement relation discovery for sequential equivalence checking" (in papers) proves that an optimized circuit is equivalent to the original specification. By automatically discovering abstraction relations (mappings from optimized signals to specification signals), the paper enables efficient equivalence checking of large designs.

"Efficient circuit verification via structure-aware SAT solving" (in papers) improves SAT (boolean satisfiability) solving — the engine beneath most formal verification — by exploiting circuit structure. Instead of treating the SAT formula as a generic Boolean formula, structure-aware SAT leverages properties of the circuit graph (e.g., circuits often have repeated sub-circuits).

#### Manufacturing Test and Defect Coverage

ATPG (automated test pattern generation) generates test patterns to detect manufacturing defects. A test pattern applies specific values to inputs and checks that outputs match expected values; if they don't, a defect is indicated.

"SAT-based ATPG with partial assignment for improved test compaction" (dac-2025-022) generates compact test patterns by formulating ATPG as SAT — finding input patterns that exercise specific faults. By allowing partial assignments (not all inputs must be specified), the pattern can be shorter and more efficient.

"Device-aware manufacturing test for unmodeled defects" (in papers) handles defects that aren't explicitly modeled. Real manufacturing defects are sometimes complex (not a simple stuck-at-one-bit fault), so test generation must handle unexpected behaviors.

### Quantum Computing (25 papers)

Quantum computing is approaching practical utility for certain algorithms, but hardware is still noisy (NISQ era — Noisy Intermediate-Scale Quantum). Papers address quantum circuit compilation, layout, error correction, and simulation.

#### Quantum Circuit Compilation and Optimization

"Depth-optimized qubit routing for NISQ circuits" (dac-2025-005) addresses qubit connectivity constraints. A logical quantum circuit assumes all-to-all connectivity, but physical devices have restricted connectivity. The compiler must route two-qubit gates (CNOT) between distant qubits via sequences of single-qubit and nearest-neighbor gates, minimizing depth (which accumulates error).

"Quantum circuit optimization via measurement-based uncomputation" (in papers) reduces circuit depth by recognizing that intermediate measurements can uncompute (erase) qubits, freeing them for reuse. This is a quantum-specific optimization with no classical analog.

#### Quantum Error Correction

"Optimized Ising decoder for quantum error correction" (in papers) addresses quantum error correction — using redundant qubits to detect and correct errors. The decoder is a classical algorithm that determines the most likely error syndrome (the pattern of measurement outcomes) and applies corrections. The paper optimizes this decoder using in-memory computing (solving an Ising model via resistive networks).

"Compressed neural networks for efficient qubit readout" (in papers) designs efficient measurement circuits. In quantum computers, readout is expensive (state-dependent leakage current, averaging to reduce noise). By compressing measurement into fewer shots (trials), quantum algorithms are more feasible.

#### Quantum Algorithms and Simulation

"Quantum autoencoder for anomaly detection" (in papers) develops a quantum machine learning algorithm for detecting anomalies in data. The paper also addresses mapping this to physical quantum hardware and handling noise.

### FPGA and Reconfigurable Architectures (57 papers)

FPGAs (field-programmable gate arrays) differ from ASICs: instead of fixed transistor layouts, FPGAs use lookup tables (LUTs) and programmable interconnect. This allows designers to implement custom circuits without fabricating a custom chip. FPGA design automation is a distinct problem space from ASIC design.

#### LUT-Based Logic Implementation

LUTs (lookup tables) map N inputs to 1 output by storing a 2^N-bit table. Multiple LUTs can be cascaded to implement larger logic functions. FPGA optimization is about packing logic into LUTs efficiently.

"DSP-block-based configurable CAM architecture for data-intensive applications on FPGA" (dac-2025-039) leverages FPGA DSP blocks (arithmetic units optimized for multiplication and accumulation) to implement content-addressable memory (CAM). CAM searches for a value in parallel across an entire array, useful for pattern matching and network routing. By cleverly using DSP blocks, the paper achieves high performance CAM on FPGA.

#### FPGA Accelerator Design

"FPGA-optimized state-space model acceleration for Mamba2" (in papers) implements the Mamba2 architecture (a recent alternative to transformers) on FPGA. State-space models are linear systems; the paper optimizes dataflow on FPGA to efficiently compute matrix products with the state-space matrices.

#### Hardened Blocks and Heterogeneous FPGA

Modern FPGAs include hardened (fixed) blocks: processors (ARM cores), DDR controllers, PCI-E interfaces. Using these blocks efficiently is critical for performance and power.

"Monolithic 3D FPGA using BEOL AOS transistors for configuration memory" (in papers) uses back-end-of-line (BEOL) transistors to implement configuration memory directly above the LUT layer, improving density. Traditional FPGAs dedicate significant area to configuration memory; this technique reduces that overhead.

### Graph Processing and GNN Acceleration (37 papers)

Graph neural networks (GNNs) operate on graph-structured data, computing node/edge embeddings via iterative neighborhood aggregation. The workload is sparse and irregular, very different from dense linear algebra in CNNs.

#### GNN-Specific Accelerators

"Stationary-data-aware PIM for GNNs via locality-preserving partitioning" (in papers) designs PIM for GNN workloads. The key insight is graph partitioning — if you partition the graph so that vertices and edges with high interaction stay together in memory, you reduce data movement. The paper combines this with PIM to perform aggregation in-place on vertices.

"GNN-enabled scalable multilevel graph partitioning with memory efficiency" (in papers) applies GNNs to the graph partitioning problem itself — using a GNN to predict good partitions. This meta-acceleration (using ML to accelerate problems similar to the ML domain) is increasingly common in DAC.

#### Sparse Tensor and SpGEMM Acceleration

Graph algorithms often reduce to sparse matrix-matrix multiplication (SpGEMM). Optimizing SpGEMM is critical.

"High-performance SpGEMM acceleration on heterogeneous Versal ACAP via block-wise storage and hybrid dataflow" (in papers) targets Xilinx Versal (a heterogeneous FPGA with hardened CPU, GPU-like vector processors, and traditional FPGA fabric). By using block-wise sparse matrix representation (storing data in blocks, which improves cache locality) and hybrid dataflow (CPU handles control, vector processors handle computation), the paper achieves high throughput.

### Vision and CNN Acceleration (109 papers)

Convolutional neural networks (CNNs) for vision are among the most-deployed ML workloads. Despite recent advances in transformers, CNNs remain fundamental for efficient edge deployment. The 109 papers in this theme cover architecture-specific acceleration, quantization, and novel network designs.

#### Efficient CNN Architectures

CNNs have high arithmetic intensity (compute-to-memory ratio) compared to transformers, making them naturally amenable to GPU and FPGA acceleration. But efficiency improvements are still valuable.

"Hardware-efficient BEV semantic segmentation via pooling and sparsity optimization" (in papers) addresses bird's-eye view (BEV) semantic segmentation — a key perception task in autonomous driving where camera images are projected to a top-down view. The paper optimizes pooling operations and exploits sparsity in the BEV (many regions are background) to achieve efficient inference.

#### Point Cloud Processing

"Hierarchical sparsity-aware point cloud 3D convolution accelerator" (in papers) accelerates 3D convolution on point clouds (sparse 3D data). By exploiting the sparsity structure (point clouds are sparse in 3D space), the accelerator skips computation for empty regions.

#### Gaussian Splatting

3D Gaussian splatting is an emerging technique for novel view synthesis (generating views of a 3D scene from arbitrary angles). It's computationally intensive but parallelizable.

"Edge accelerator for Gaussian splatting training with order-independent rendering" (in papers) implements Gaussian splatting training on edge devices. By using order-independent rendering (splatting in any order, not just front-to-back), the accelerator is more parallelizable and efficient.

### Scheduling and Task Orchestration (108 papers)

Scheduling is the problem of assigning tasks (operations) to resources (functional units) and time steps (clock cycles or nanoseconds). For hardware accelerators, this is hardware scheduling (dataflow mapping); for software, this is OS scheduling. At DAC, both are represented.

#### Dataflow Scheduling for Accelerators

Dataflow graphs represent computations where nodes are operations and edges are data dependencies. Scheduling assigns each node to a resource and time step, respecting dependencies and resource constraints.

"DARIS: An Oversubscribed Spatio-Temporal Scheduler for Real-Time DNN Inference" (dac-2025-007) schedules DNN operations on heterogeneous hardware (CPU, GPU, NPU). The novelty is oversubscribed scheduling — allowing more tasks than resources, with the scheduler managing the oversubscription. This is valuable for real-time systems where missing a deadline is catastrophic (e.g., autonomous driving).

"Decoupled access/execute for DNN dataflow accelerators with programmable streaming" (in papers) separates memory access from computation in dataflow scheduling. By decoupling these, the scheduler can overlap data fetches with computation for other operations, improving utilization.

#### Task Placement and Load Balancing

"Bottleneck-aware asymmetric auto-scaling for multi-accelerator edge ML inference" (in papers) recognizes that different DNNs have different bottlenecks — some are memory-bound, others compute-bound. By profiling the bottleneck and adapting resource allocation (e.g., using more bandwidth for memory-bound tasks), the paper improves throughput under fixed power budgets.

#### Compiler-Driven Scheduling

Some papers combine compilation with scheduling, recognizing that the order in which operations are generated affects scheduling efficiency.

"PTX-level kernel fusion via instruction flow weaving for ILP improvement" (in papers) fuses multiple GPU kernels (functions) by interleaving their instructions. This improves instruction-level parallelism (ILP) and reduces memory stalls.

### Specialized Hardware Paradigms (31 papers)

Beyond traditional digital CMOS, there are emerging paradigms: analog computing, photonic computing, neuromorphic computing (event-driven, inspired by biology), and quantum.

#### Analog In-Memory Computing

Analog computation is more energy-efficient than digital (not constrained by binary precision), but less accurate. Recent work explores analog for problems that tolerate approximation.

"Time-domain universal nonlinear operator for integrated analog computing" (dac-2025-025) designs an analog circuit that implements arbitrary nonlinear functions (e.g., sigmoid, ReLU). By using time-domain analog (representing values as time intervals rather than voltages), the circuit is robust to process variation.

#### Photonic Computing

"P-DAC: Power-Efficient Photonic Accelerators for LLM Inference" (dac-2025-021) uses photons (light) for computation, leveraging the high speed and low energy of optical systems. Photonic matrix multiplication can be implemented with a photonic programmable processor, and the paper designs power-efficient implementations for LLM.

#### Neuromorphic Computing

Neuromorphic systems are inspired by biological brains — they compute using spikes (events) rather than continuous values. This enables extreme sparsity (no computation when no spikes).

"Maximizing Energy Efficiency in Spiking Neural Networks: A Dynamic Joint Pruning of Spatiotemporal and Weight Sparsity for Energy-Efficient SNN Inference" (dac-2025-032) optimizes SNNs by exploiting both weight sparsity (many synapses have zero weight) and temporal sparsity (most neurons don't spike at each time step). The accelerator skips computations for zero weights and silent neurons.

### Interconnect and Network-On-Chip (13 papers)

Chips with billions of transistors have thousands of cores or millions of memory cells. Connecting them efficiently is non-trivial. Network-on-chip (NoC) provides a network-like communication infrastructure inside the chip.

#### Optical NoC

"Variation-aware optical NoC design via joint MRR and wavelength optimization" (in papers) designs optical networks inside chips using microring resonators (MRRs) to multiplex wavelengths. Unlike electrical interconnect, optical is low-latency and high-bandwidth but requires careful tuning to process variations.

#### NoC Topology and Routing

Papers on NoC topology exploration, adaptive routing, and congestion management address how to design efficient interconnects for many-core systems. Most focus on reducing hop count (number of switches traversed) and balancing load.

### Chiplets, 3D Integration, and Heterogeneous Systems (8 papers)

Chiplets are small chips bonded together using technologies like hybrid bonding (Cu-Cu) or micro-bumps. This allows mixing different technologies (e.g., logic at 5nm, memory at older nodes) and improves yield (smaller dies have fewer defects).

#### Chiplet Assembly and Integration

"Analytical yield model for Cu-Cu hybrid bonding in chiplet integration" (in papers) models the yield (fraction of working chips) of chiplet assemblies, accounting for hybrid bonding defects. This enables designing chiplets for maximum yield.

#### Heterogeneous System Design

"Eda methodology framework for chiplet-based heterogeneous system design" (in papers) provides a comprehensive EDA flow for chiplet systems, including partitioning the design into chiplets, handling chiplet-specific design rules, and integrating heterogeneous chiplets.

## Cross-cutting patterns

Across the 442 papers and 25 themes, several patterns emerge:

**Learning-Based Optimization**: Machine learning (particularly neural networks and reinforcement learning) is increasingly used to guide EDA optimization. Rather than hand-crafting objective functions and heuristics, researchers train models to predict outcomes (delay, power, timing closure success) and use these predictions to guide search. Examples include RL-based placement optimization, neural networks predicting power/timing, and diffusion models for generation (floorplanning, circuit generation).

**Hardware-Software Co-Design**: The tight integration between algorithmic efficiency (precision, sparsity, dataflow) and hardware implementation is pervasive. Papers rarely optimize algorithm or hardware in isolation; instead, they co-design both. This is visible in quantization-hardware co-design, dataflow-architecture co-design, and application-specific ISA design.

**Workload-Specific Optimization**: Rather than general-purpose solutions, papers increasingly target specific workloads (LLM inference, graph processing, imaging) with specialized hardware and algorithms. This follows the broader trend in industry toward application-specific accelerators (TPUs, NPUs, inference engines) rather than general-purpose CPUs.

**Precision and Approximation as First-Class Citizens**: Low-precision arithmetic, approximate computing, and error tolerance are no longer edge cases but mainstream. Quantization to INT4 or lower, floating-point custom formats, and stochastic computing are accepted as necessary for efficiency. The challenge shifts from "how do we compute exactly" to "how do we maintain accuracy while using minimal precision."

**Data Movement as Primary Cost**: Design decisions increasingly privilege reducing data movement over reducing compute. This manifests as PIM, CIM, in-memory optimization, and cache-hierarchy co-design. The understanding that moving a bit costs more than computing a result is now foundational.

## How DAC fits in the ecosystem

DAC outputs tools, methodologies, and insights that flow downstream to chip design teams at major semiconductor companies (TSMC, Samsung, Intel, NVIDIA) and fabless design houses (Qualcomm, Apple, AMD, AWS Trainium team). A breakthrough in placement optimization or timing analysis directly impacts how millions of chips are designed.

Upstream, DAC depends on device physics (from materials science and physics conferences like IEDM), algorithms and learning methods (from ML conferences like NeurIPS and ICML), and software engineering practices (from systems conferences like OSDI and SOSP). DAC is the integration point where these flow together.

DAC does **not** typically address: high-level architecture design (that's ASPLOS/ISCA), OS and software system design (SOSP/OSDI), algorithms for specific applications (NeurIPS), or device-level physics (IEDM). Instead, it assumes high-level intent (a specification or architecture) and focuses on automating its translation to silicon.

## What is not yet solved

Two large gaps are visible in the 2025 corpus:

**Design Closure Automation Under Uncertainty**: Current tools assume relatively well-specified constraints (timing, power, area targets). In practice, designers don't know exact targets a priori — targets are negotiated based on what's achievable. Automated exploration of tradeoff surfaces (Pareto frontiers of delay vs. power vs. area) is still manual and slow. Ideally, a designer would describe intent (e.g., "prioritize LLM inference throughput, accept 2x power vs. baseline") and EDA tools would autonomously explore solutions. This requires not just optimization but also **multi-objective design space exploration with human-in-the-loop**.

**Handling Uncertainty and Variation**: Process variation (transistor properties vary by 10-30% across a wafer), thermal gradients (some parts of the chip are hotter), voltage droop (power supply dips under high current), and aging (transistors degrade over time) all create uncertainty. Current tools use worst-case pessimism (design for corner conditions), but this wastes area and power on chips that don't experience the worst case. Adaptive techniques (on-chip tuning, dynamic margin adjustment) are nascent. Deep integration of in-field adaptation with design-time analysis is underexplored.

**Verification of Complex Behaviors**: Formal verification scales to millions of gates but not billions. Most verification relies on simulation, which can miss corner cases. Ensuring correctness of billion-transistor designs with complex cache hierarchies, speculative execution, and concurrency is fundamentally hard and often done by assuming components are correct (trusting prior verification). A unified framework for partial verification (proving properties of sub-systems) and compositional verification (proving system-level properties from subsystem properties) remains elusive.

---

**Analysis complete.** DAC 2025 represents the state of the art in automated chip design under tightening constraints: higher AI workload diversity, extreme process variation, escalating power density, and pressure to shorten design time. The solutions reflect a field maturing toward practical deployment, data-driven optimization, and embracing approximation as a core design philosophy.
