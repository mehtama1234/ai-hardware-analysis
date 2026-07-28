# DAC 2025: The Core Problem of Chip Design Under Constraint

## What DAC is

DAC (Design Automation Conference) exists to solve a specific problem that no other venue addresses at its scale: **how do you automatically design, verify, and optimize the billions of transistors in a chip when you have competing objectives that cannot all be satisfied simultaneously?** This is not a research community. It is an engineering community. The papers here are not theoretical; they are practical solutions to bottlenecks that block production silicon from shipping. Attendees are the people writing EDA tools at Cadence, Synopsys, and Intel; design teams at TSMC, Samsung, and Apple; and academics who partner with industry to unblock real design flows. DAC accepts papers on formal verification, circuit synthesis, physical design (placement and routing), timing analysis, power estimation, and the increasingly critical layer: hardware-software co-design. It is the only venue where a paper on how to better arrange transistors in 3D shares the program with a paper on how to deploy LLMs safely in silicon—because both block tape-out. The reason DAC exists is that chip design is intractable without automation, and automation is useless without knowing which trade-offs actually matter.

## The one problem this community is organized around

Modern chips contain 10 billion to 100 billion transistors. Designing them by hand is impossible. But automation has a hard constraint: each decision ripples through downstream tools. When a logic synthesis tool makes a gate replacement to reduce area, it changes the wiring, which affects power delivery, which can cause timing violations. When a physical design tool places a memory macrocell to minimize wirelength, it creates thermal hotspots, which throttle performance. When a compiler generates code that accesses memory in a particular pattern, it changes the stress on the cache and interconnect, which can make the entire system bottlenecked on one resource instead of another.

The fundamental problem is **resource contention and multi-objective optimization under incomplete information.** The designer wants the chip to be fast (low latency), power-efficient (low energy), small (high area efficiency), manufacturable (no yield loss), and secure (resistant to side-channel attacks). These objectives directly conflict. Making something faster usually requires more power. Making it smaller usually hurts timing or reliability. Making it secure often adds latency or area.

Classical optimization theory says: compute all Pareto-optimal solutions, then choose the one that matches your deployment constraints. But chip design does not work this way. You cannot compute the true latency of a design until you have done physical placement and routing—but placement takes hours, and you need to evaluate thousands of candidates. You cannot know the true power dissipation until you have extracted parasitic capacitance from the layout—but parasitic extraction is expensive and couples to timing analysis, which couples to logic synthesis. This is called the **modeling gap**: the more accurate your model, the longer it takes to run, and chip designers have a fixed time budget before tape-out (12-18 months, typically).

DAC exists because solving this problem requires not just algorithmic cleverness, but **domain-specific insight into which models to use at which stage, how to detect when a local decision will cause a global failure downstream, and when to abandon a promising candidate design to avoid wasting hours on a doomed path.** The community focuses on reducing the cost of iteration, improving the quality of early predictions, and decomposing the problem into sub-problems that can be solved in parallel without synchronization deadlocks.

## The main approaches in 2025

### Fast and accurate modeling with learned surrogates

The oldest approach: instead of running the full tool flow, train a neural network to predict the outcome (timing, power, area) in milliseconds instead of hours. Papers like "LLM-enhanced Bayesian optimization for microarchitecture design space exploration" and "few-shot meta-learning for efficient CPU design space exploration" train models on historical design data to predict performance without simulation. The recent shift is toward multi-modal models: "CNN-GNN fusion for IR drop prediction" uses graph neural networks to encode circuit topology and convolutional networks to capture spatial patterns in power density.

The challenge: learned models are only valid within the domain of designs they were trained on. A model trained on 16nm designs fails on 3nm designs. A model trained on dense logic fails on memory-heavy designs. The 2025 papers show the community betting on *transfer learning* and *meta-learning*—training on diverse datasets, then fine-tuning on new design families with just a few examples. This works well for timing (continuous function, smooth gradients) but poorly for discrete properties like manufacturing yield.

### Hardware-software co-design: closing the stack

The most important trend: **moving optimization earlier by co-designing hardware and software together.** "Multimodal machine learning for adaptive spMV selection" trains a classifier to decide at *runtime* which sparse matrix-vector multiplication kernel to use based on the actual sparsity pattern. "Real-time proxy-free ISP tuning via distributed DRL for autonomous vision systems" optimizes the image signal processor (ISP) settings dynamically for the current camera input, rather than committing to fixed settings at design time.

The fundamental insight: a 5% area reduction in hardware is worthless if the compiler generates worse code. A compiler optimization that saves 20% energy is blocked if the hardware cannot express the parallelism efficiently. Papers like "input-aware vectorized compilation for efficient sparse tensor operations" show the payoff: by having the compiler analyze the input data structure (sparsity pattern, memory layout) and *specialize* the vector instructions, they achieve 2-3x speedup over generic compilation. This requires tight coupling between the EDA tool and the compiler; DAC papers increasingly show this boundary dissolving.

### In-memory and near-data processing: moving computation to where the data lives

Historically, chips were designed with a sharp separation: CPU (logic), memory (storage), interconnect (wires). Modern chips are breaking this boundary by adding compute to memory locations. "Dual-mode PIM architecture for asymmetric LLM attention GEMV" embeds processing elements in the memory array itself to accelerate matrix-vector multiplication with minimal data movement. "Hierarchical in-memory acceleration for ANNs via bank/controller-level partitioning" uses different memory levels (DRAM rows, banks, controllers) as compute resources.

Why now? AI workloads are memory-bound: a 100 billion parameter LLM needs to load 200 GB of weights from memory, which takes longer than the actual arithmetic. By moving compute into the memory system, you eliminate the data movement bottleneck. The trade-off: PIM requires custom hardware and custom code. A paper like "Retrieval-in-memory architecture for efficient RAG inference via hierarchical PIM dataflow" shows the payoff: 10-20x speedup on RAG queries by using hierarchical PIM. But only for specific workloads. This requires careful partitioning of the algorithm into memory-near operations (simple operations, high data locality) and off-array operations (complex control flow).

### Formal verification: proving correctness instead of testing

A chip with a functional bug cannot be recalled. The team must catch it before tape-out. Testing alone is insufficient: you can test billions of input combinations and still miss a corner case. Formal verification proves that a design meets a *specification* (a mathematical formula) for all possible inputs.

Papers like "Proof-obligation optimization for IC3 verification" and "Automated refinement relation discovery for sequential equivalence checking" show the field shifting from checking individual properties ("does the output register load the right value?") to *compositional* verification (proving that a module meets its contract, then composing modules into higher-level guarantees). The bottleneck is proving complexity: proving that a 10-million-gate design meets 100 properties can take weeks, even with parallelization.

The 2025 breakthrough is using SAT solvers and SMT solvers as *components* of larger search procedures, rather than the end-to-end tool. "Adaptive ASIC SAT accelerator with in-memory computing" is an ASIC that runs SAT on chip, accelerating verification by 90x for certain problem classes. "Hashing-based approximate SMT model counting for hybrid formulas" shows that sometimes you don't need *perfect* verification—approximate counts of satisfying assignments are good enough for risk assessment on automotive or medical chips.

### Compiler and synthesis driven by learned policies

Instead of hand-coded heuristics ("prefer short wires," "avoid tall logic trees"), use reinforcement learning to discover what works. "RL-guided logic synthesis for efficient circuit-SAT preprocessing" trains an agent to decide which transformation to apply to a logic circuit. "RL-driven window selection for detailed routing optimization" learns which region of the chip to route next to minimize congestion.

The pattern: RL works well when the state space is rich (routing has millions of possible next states) and feedback is fast (you can run 10,000 routing experiments overnight). RL fails when feedback is slow: training an RL policy for chip floorplanning (where each evaluation takes hours) is impractical.

### LLM-based code generation and automation

The newest and most controversial approach: use LLMs to *generate* chip designs directly from specifications. "LLMs as transformative agents in silicon design automation" and "Multi-agent LLM system for correct Verilog RTL generation" show teams training LLMs (fine-tuned Llama, GPT) to generate Verilog code, RTL, even testbenches. The challenge: LLMs hallucinate. "Free and fair hardware: copyright infringement-free Verilog generation" shows that models trained on public code repositories inherit copyright-protected designs unless you curate the training data carefully.

The real opportunity is not *replacing* designers but *accelerating* routine tasks. Generating boilerplate register files, memory interfaces, or standard cell placement rules from natural language takes minutes instead of hours. Designers use the time saved for higher-level system architecture or debugging subtle edge cases.

## How it connects to the broader field

DAC is downstream of the computer architecture community (ISCA, MICRO, HPCA). Those venues design algorithms and processor cores. DAC takes those designs and implements them efficiently on silicon. DAC is upstream of the machine learning community: once a chip is designed and taped out, ML researchers run experiments on it and discover new workloads (LLM inference, GNNs), which feed back into DAC as new design constraints.

DAC is also tightly coupled with the verification community (FMCAD, CAV): formal methods research proves properties; DAC papers apply those methods at scale to real designs. And it is linked to the systems community (OSDI, SOSP): a breakthrough in chip-level cache coherence protocol (DAC) enables a new distributed memory algorithm (SOSP).

What DAC does *not* do: it does not design new circuit physics (that is IEDM, VLSI Symposium). It does not design chip packaging or mechanical integration (that is IEEE 3D Systems Integration). It does not design the software that runs *on* the chip after it ships (that is PLDI, ASPLOS). DAC's scope is the tools and algorithms that sit in the middle: taking a high-level algorithm and silicon physics, and producing a design that is correct, efficient, and manufacturable.

## What's open

The most honest gap: **the 12-18 month design cycle has not shrunk in 20 years, despite exponential improvements in tools.** Parallelization has hit hard limits. Physical design tasks (placement, routing, timing closure) are inherently sequential: earlier decisions constrain later ones. Early estimates are so inaccurate that teams must re-do logic synthesis and placement multiple times as they learn what actually fits. The community is still predominantly using greedy local search (gradient descent, simulated annealing) because global optimization is NP-hard. Until someone breaks the sequential bottleneck—perhaps by learning to predict the final timing of a placement in milliseconds without actually placing it—the design cycle will remain a bottleneck for all of computing.

A second gap: **security is still a bolt-on.** Most chips are designed for performance and power, then security is added via afterthought: add a TEE here, encrypt that bus there. Papers on side-channel attacks ("Rowhammer-based side-channel attack on zero-knowledge proofs," "LLC side-channel attacks on AMD Zen processors") are growing, but papers on *designing* chips to be secure from the start are rare. The community has not yet solved security-by-design at scale; most papers treat it as a constraint to respect, not an objective to optimize for.

Finally: **the design of specialized hardware for AI is still fragmented.** Every company (NVIDIA, Apple, Google, Meta, Tesla) is building their own LLM accelerator, their own GNN accelerator, their own recommendation system accelerator. There are no standard abstractions or reusable components. Each team re-solves the same sub-problems: how to efficiently serve long-context LLM inference, how to schedule sparse operations on dense hardware, how to avoid memory bandwidth bottlenecks. The community talks about hardware standardization (OCP, open standards for interconnect) but has not converged. This is partly intentional—competitive differentiation—but it means vast duplication of effort and missed opportunities for tools and methodologies to amortize across designs.
