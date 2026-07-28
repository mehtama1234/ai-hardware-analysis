# VLSID 2025 — Deep Dive

## What VLSID is and why it exists

The Very Large Scale Integration Design (VLSID) conference exists at a critical inflection in semiconductor history. Unlike architecture or algorithm conferences that ask "what should we compute," VLSID answers "how do we build it—with real constraints." The conference brings together RTL designers, EDA tool developers, circuit engineers, and physical design specialists to solve the unglamorous but essential problem: getting bits to move through silicon efficiently, reliably, and without burning the die.

VLSID is the venue for the practitioners who inherit the computational ambitions of the AI boom and face the physics directly. A paper on pruning neural networks becomes a design problem when you must fit a quantized model into 2 MB of embedded memory. A paper claiming 10 TFLOPS on a hypothetical dataflow becomes a verification problem when you simulate that dataflow in RTL for 14 days straight. VLSID 2025's 97-paper program reflects this grounded reality: the conference has absorbed a wave of AI acceleration work, but the core concerns—power, area, reliability, verification, and manufacturability—remain unchanged.

The conference draws primarily from Indian academia and industry, but increasingly hosts international submissions. The venue provides a rare space where a paper on FPGA arithmetic design sits alongside work on neuromorphic computing, quantum error correction hardware, and secure memory systems. This diversity stems from VLSID's founding principle: that semiconductor design is a unified discipline spanning analog, digital, memory, and increasingly, novel computation paradigms—all subject to the same area-power-timing trilemma.

VLSID 2025 mirrors the semiconductor industry's current state. The easy scaling laws have stopped. Transistor density still improves, but power density soars, reliability edges toward unmanageable, and yield becomes a process variation lottery. The conference's program reflects designers asking harder questions: How do we build neuromorphic systems that exploit analog physics for efficiency? How do we verify AI accelerators when the dataflow is irregular? How do we secure hardware when side-channel attacks are physics, not bugs? How do we power and cool massive compute clusters? The breadth of VLSID's themes shows that industry and academia see design—not just architecture or algorithms—as the frontier.

## The core constraint

The fundamental constraint that unifies all 97 papers in VLSID 2025 is simple to state but brutal in practice: **you can make circuits smaller, faster, or lower-power than today, but you cannot optimize all three at once when you must also guarantee correctness, reliability, and manufacturability.**

This is not a limitation of current technology but a law of physics and information theory. Smaller transistors switch faster but leak more current. Faster circuits require tighter power delivery and dissipate heat more densely. Lower-power designs sacrifice parallelism or precision, creating correctness problems. Reliable circuits need redundancy and error correction, which consumes area and power. Manufacturable circuits must tolerate process variation, which forces guard-banding and headroom. Each choice forecloses others.

The scaling argument is deceptively obvious: TSMC 3 nm chips are real, but they are not 10 times cheaper, 10 times smaller, or 10 times more power-efficient than 7 nm chips. The promise of Moore's Law—exponential improvement in transistor count per unit area—continues, but the productivity per transistor has stalled. A 3 nm transistor is smaller in absolute dimensions but provides only marginal benefit because the design must accommodate higher leakage, greater process variation, more electromigration risk, and tighter signal integrity margins. The "cost per transistor" metric obscures the true cost: design complexity, verification effort, power management circuits, and yield loss all scale with chip complexity.

The power wall manifests differently across design contexts. In high-performance datacenters, a single GPU die can consume 400+ watts. The memory subsystem alone draws 30–50% of total power, but moving data is thermodynamically cheap compared to the arithmetic—a multiply-accumulate (MAC) operation in floating-point might consume 10–100 femtojoules, but moving that data across a chip costs comparable energy. In edge AI accelerators, the budget drops to milliwatts. A wearable device with a 500 mAh battery must run neural network inference continuously for weeks; a 100 mW average budget means every gate must earn its power draw. These contexts generate entirely different design methodologies: the datacenter design tolerates complexity to maximize throughput, while the wearable design sacrifices latency and precision to stay under power.

Verification represents a hidden constraint that compounds others. A small, low-power design is not useful if it computes wrong answers. VLSID papers on formal verification, simulation acceleration, and ML-guided coverage closure acknowledge a uncomfortable truth: verification effort scales superlinearly with design complexity. A 100M-transistor AI accelerator requires not just logic simulation but transaction-level modeling, power integrity analysis, timing closure verification, functional equivalence checks, and corner case exploration. A typical tape-out requires millions of simulation vectors and days of compute. This verification budget is a real cost—it delays time-to-market, consumes engineering resources, and sometimes reveals that a clever optimization is unmeetable in silicon.

Reliability and yield emerge as dominant constraints in advanced nodes. A 3 nm FinFET transistor is exquisitely sensitive to process variation: threshold voltage (Vt) can shift by 50–100 mV across a die due to random dopant fluctuation, line-edge roughness, and metal grain size. This variation forces designers to build circuits that work across a 5× range in leakage current and a 3× range in propagation delay. Yield loss—the fraction of manufactured dies that meet specifications—can reach 20–30% at node transitions, driven by random defects (open vias, missing contacts) and parametric failures (timing, leakage). A design that optimizes peak performance but yields at 50% is an economic failure.

The interdependence of constraints amplifies the challenge. Lowering voltage to cut power increases susceptibility to noise and variation. Adding error correction for reliability consumes 5–20% area overhead. Hardening against process variation requires guard-banding that sacrifices 10–20% of available frequency or power. These tradeoffs cascade: a 10% power reduction via voltage scaling might require 5% additional area for power delivery, 8% for noise filtering, and 15% for timing margin to tolerate increased delay variation. The total design cost is not 10% but often 40–60%.

Design automation—EDA tools—becomes a force multiplier but introduces its own constraint: tool capability limits design ambition. No practical EDA tool solves the full power-timing-area optimization problem globally. Instead, tools operate in phases: synthesis (logic optimization), placement (spatial arrangement), routing (interconnect), and verification (checking). Suboptimal handoffs between phases leak efficiency. A circuit routed for minimum wirelength might have terrible power delivery; a power grid designed first might constrain routing. These sequential approximations mean actual silicon is always worse than the theoretical minimum.

The constraint applies across workloads and technologies in VLSID's portfolio. Whether designing an ASIC for LLM training, an FPGA for edge inference, a neuromorphic processor, or an RF energy harvester, every design must navigate the power-area-timing trilemma, verification burden, and yield reality. The papers in VLSID 2025 reflect not the absence of this constraint but rather creative problem-solving within it: approximate computing trades correctness for efficiency; neuromorphic design exploits analog physics to reduce power; formal verification catches bugs before silicon; specialized accelerators reduce verification scope by accepting application specificity.

## Themes and subthemes

### AI/ML Hardware Acceleration
The largest and fastest-growing category in VLSID 2025 encompasses dedicated hardware for neural networks and machine learning. This is where AI architecture meets silicon reality—the papers here confront the gap between theoretical performance and real deployments.

#### In-Memory Computing and Specialized Datapaths
Papers in this subtheme address the memory wall—the observation that fetching a value from main memory costs 10–100× more energy than performing arithmetic on it. Solutions include compute-in-memory (CIM) where operations occur at or near the memory array, and specialized arithmetic units optimized for neural network operations. *TimeFloats: Train-in-Memory with Time-Domain Floating-Point Scalar Products* proposes a novel number representation that amortizes arithmetic costs across time-domain encoding, reducing area and power for training. *A 14-nm Energy-Efficient and Reconfigurable Analog Current-Domain In-Memory Compute SRAM* demonstrates analog CIM with SRAM, accepting approximate results to achieve orders-of-magnitude improvements in energy per operation. These designs trade precision and flexibility for dramatic efficiency gains, accepting 8–16 bit quantization rather than 32-bit floats and committing to specific workload patterns rather than supporting arbitrary code.

The fundamental insight is that if 95% of neural network operations are simple dot-products on quantized data, building custom silicon for exactly that operation beats general-purpose processors. A systolic array of 8-bit multiply-accumulate units with local memory achieves 10× better energy efficiency than a CPU cache hierarchy executing the same workload. But this specialization creates its own cost: design complexity skyrockets. A flexible datapath with register files, control logic, and memory interfaces is easier to verify than a spatial array of thousands of identical PEs with intricate dataflow orchestration.

#### Edge AI Inference
Edge AI papers focus on inference (not training) on resource-constrained devices: smartphones, smart watches, IoT devices, or UAVs. The primary objectives differ from datacenters: latency matters less than throughput per watt, area-per-inference is paramount, and the ability to run continuously on battery defines viability. *LO-SC: Local-Only Split Computing for Accurate Deep Learning on Edge Devices* proposes a split-inference strategy where some layers run locally and others offload to edge servers, achieving lower latency than full cloud inference without the bandwidth cost of full device offload. This requires careful management of model partitioning, data movement, and synchronization.

Edge AI papers also grapple with model compression: quantization to 4-8 bits, pruning 80%+ of weights, and knowledge distillation to create smaller student models. Hardware must support varied precisions and irregular sparsity patterns efficiently. A network quantized to 4-bit integers cannot use a datapath built for 8-bit arithmetic without wasting area; but providing a fully flexible multi-precision datapath adds overhead that defeats the compression goal. The papers here describe partial solutions: tunable quantization aware of hardware capabilities, sparse memory access patterns that exploit structure in weights, or approximate activations that tolerate lower precision.

#### DNN Training Hardware
While most AI accelerators target inference, a few papers target training—the process of updating weights. Training is 10–100× more computationally expensive than inference and requires higher precision (typically 16–32 bit) to avoid divergence. The core bottleneck is not computation but data movement: a GPU spends 60–80% of execution time moving data between memory and compute, and improving this ratio requires either higher bandwidth (expensive, power-hungry) or lower-precision arithmetic (risks training stability).

#### Neural Architecture and Dataflow Optimization
Papers like *E-DOSA: Efficient Dataflow for Optimising SNN Acceleration* focus on the intersection of algorithm and hardware: how to map neural network operations to hardware resources to minimize data movement and communication. This requires joint optimization—deciding which neurons run on which PEs, which data stays in local memory, and when to synchronize. The space is vast: an accelerator for a 1000-neuron SNN might have 1000 possible dataflow mappings, each with different area, power, and latency tradeoffs. Automated design-space exploration tools (often using ML to guide the search) have become essential.

### Hardware Security and Trust
Security in semiconductors spans three domains: preventing side-channel attacks (extracting secrets by measuring power, timing, or electromagnetic radiation), protecting IP (preventing cloning or reverse-engineering), and ensuring integrity (preventing transient faults from corrupting computation).

#### Side-Channel Attack Mitigation
A side-channel attack exploits physical properties of hardware rather than algorithmic weaknesses. A cryptographic accelerator might use constant-time algorithms to prevent timing analysis, but the power consumption during a multiply operation can reveal the operand bits. Mitigation strategies include: power randomization (adding dummy operations to mask real power), constant-area circuits (all paths take identical area regardless of logic values), differential logic (complementary logic that draws constant current), and noise insertion (adding noise large enough to overwhelm signal). These defenses increase area by 10–50% and power by 5–20%, raising the cost of security.

Papers in this subtheme—*Codesign for Broadcast Addressing Biochip Towards Tamper-Resistance and Enhanced Reliability*—investigate both passive defenses (circuit design for low side-channel leakage) and active defenses (detecting and responding to attacks). The papers often focus on lightweight cryptography (AES, SHA-256) for IoT and wearable devices where silicon area is severely constrained.

#### Logic Obfuscation and IP Protection
Designers fear reverse-engineering and IP theft, especially for custom accelerators and ASICs. *SHAKTI: Securing Hardware IPs by Cascade Gated Multiplexer-Based Logic Obfuscation* proposes obfuscating the RTL by inserting programmable multiplexers that modify circuit behavior based on a secret key. The obfuscated circuit behaves correctly only if the key is applied during manufacturing; without the key, it produces garbage. This prevents third-party foundries from understanding the design and cloning it. The cost is modest area overhead (10–15%) but creates new verification challenges: is the obfuscated circuit equivalent to the original? Formal verification tools must prove this while treating the key as symbolic (unknown).

#### Integrity Verification for Secure Memory
As machine learning models become valuable IP, protecting model weights in memory becomes critical. Untrusted endpoints (edge devices) might be subject to fault injection attacks: bombarding memory with laser pulses to bit-flip values. *ABMF: Adaptive Bonsai Merkle Forests for Efficient Integrity Verification in Secure Persistent Memory* proposes a tree-based integrity structure where leaf nodes hash memory blocks and internal nodes hash their children. This allows detecting any corruption by verifying only log(N) hashes. The overhead is low (< 10% memory) but requires careful integration with memory controllers and caches.

### Neuromorphic and Event-Driven Computing
Neuromorphic computing mimics biological brains by using event-driven updates (neurons fire only when they exceed a threshold) rather than synchronous clocking. This creates an opportunity: if neurons spike 5% of the time, you perform 5% of the arithmetic, using only 5% of the power. The catch is architectural: event-driven systems require different programming models, verification is harder (no global clock means no deterministic state), and exploiting sparsity in hardware is tricky.

#### Spiking Neural Networks (SNNs)
SNNs compute with temporal information encoded in spike timing rather than analog values. A neuron integrates incoming spikes and fires when the membrane potential exceeds a threshold. This is closer to biological computation and, more importantly for hardware, exploits sparsity: most neurons are inactive at any moment. *Bidirectional Spiking Neuron Based Dual-Mode Signal Acquisition Front-End System* demonstrates a mixed-signal front-end that acquires analog sensor data and converts it to spikes, enabling energy-efficient signal processing.

The hardware challenge is routing: in a traditional ANN accelerator, data flows from layer to layer in a predictable pattern. In an SNN, spikes are irregular events that must be routed to destination neurons dynamically. This requires a NoC (network-on-chip) with event routing, or significant on-chip memory to buffer spike events. *E-DOSA: Efficient Dataflow for Optimising SNN Acceleration* addresses this by co-optimizing SNN algorithms and hardware dataflows, deciding which neurons to assign to which PEs to minimize spike communication.

#### Analog Neuromorphic Circuits
Some groups build neuromorphic processors with analog neurons—circuits that physically integrate and threshold. These can be 100× more efficient than digital implementations but are difficult to design (analog design requires expertise) and cannot be easily modified in software. Papers in this space focus on robust circuit design for analog neurons in noisy conditions and verification that the analog behavior matches the intended SNN algorithm.

### FPGA Design and Reconfigurable Hardware
FPGAs provide a middle ground between ASICs and CPUs: programmable at the hardware level, they offer better efficiency than CPUs but more flexibility than ASICs. VLSID 2025 includes papers on optimizing FPGA implementations for specific workloads.

#### Arithmetic Optimization on FPGAs
FPGAs are composed of look-up tables (LUTs) and block RAMs (BRAMs). Mapping arithmetic operations (multipliers, adders) to these primitives efficiently is non-trivial. *Leveraging Dual Output LUTs with Pipelining for Efficient BCD to Binary Converter on FPGA* demonstrates how to exploit FPGA features (dual-output LUTs allow two independent functions per LUT) to implement custom arithmetic more efficiently than generic implementations. This requires detailed knowledge of the target FPGA architecture and is often done by hand or using specialized synthesis tools.

#### Reconfigurable Accelerators
Some papers describe FPGAs reconfigured per-task: a machine learning task might reprogram the FPGA to change datapath configuration, memory layout, or communication patterns. This flexibility is powerful but creates verification challenges: the system must guarantee that all possible configurations are correct, not just a few tested instances.

### Design Verification and Formal Methods
Verification—ensuring hardware correctness before tape-out—is a bottleneck. As designs grow, the simulation space explodes exponentially. A 64-bit counter has 2^64 possible states; a design with 100M transistors might have 2^1000 reachable states. Simulation can only explore a tiny fraction.

#### Machine Learning for Verification Acceleration
Traditional verification uses random testing, pseudo-random testing guided by coverage metrics, or formal model checking (exhaustively exploring the state space). New approaches use ML to guide the search: if most bugs appear when certain signals are correlated (e.g., high address and high data value), an ML model can learn these patterns and generate tests that trigger them. *Accelerated Design Verification Coverage Closure Using Machine Learning* demonstrates that ML can reduce verification time by 20–40% by learning patterns in failed tests.

The limitation is that ML is trained on past designs; it must generalize to new designs. And ML cannot prove correctness—it can find bugs faster but cannot prove their absence.

#### Formal Verification of Arithmetic Circuits
*FARAD: Automated Formal Verification of Approximate Restoring Array Dividers* tackles verifying an approximate arithmetic circuit (a divider that trades accuracy for area/speed). Formal verification tools must check if the circuit's behavior stays within specified error bounds across all inputs. This is non-trivial: the state space is large, and proving properties about floating-point arithmetic is subtle.

#### Post-Silicon Validation
Even after simulation, bugs can escape to silicon. *AI-Driven Anomaly Detection in Oscilloscope Images for Post-Silicon Validation* uses machine vision to detect anomalies in oscilloscope traces of silicon. This combines image recognition with domain expertise: an ML model is trained to recognize patterns that correspond to design flaws (signal integrity issues, timing violations), then applied to live oscilloscope data from test chips.

### Low-Power and Energy-Efficient Design
Power consumption dominates cost in many domains: battery life in mobile, total-cost-of-ownership in datacenters, and manufacturability in high-density chips. VLSID 2025 includes papers on power reduction across the stack.

#### Ultra-Low-Power Circuits
Wearable devices and IoT sensors often run on coin-cell batteries; available power is microwatts. *A Wide Dynamic Range Differential Drive CMOS Rectifier for μWatts RF Energy Harvesting Systems* harvests ambient RF energy (e.g., from cellular towers) and converts it to usable power. The rectifier circuit must operate with input voltages as small as 100 mV, requiring careful circuit design and layout. At these scales, subthreshold operation (running transistors below the threshold voltage) and near-threshold logic (operating at minimum voltage for function) become essential.

#### Approximate Computing
If 1 error per 1000 operations is acceptable (often true in machine learning, image processing, signal processing), then circuits can trade accuracy for efficiency. Approximate adders use shorter logic chains and accept occasional errors. Approximate multipliers reduce the number of partial products. *An Innovative Solution to Improve Ultra Low Voltage Writability and Leakage in GPU SRAMs* explores a tradeoff: SRAMs at ultra-low voltage become unreliable, but accepting soft errors (transient bit flips) and using error correction allows running at 40% lower voltage, saving 50%+ power.

#### Power Management Circuits
Complex chips require multiple on-die voltage domains and dynamic voltage/frequency scaling. *A Fully Autonomous 1.2A Auxiliary Buck DC-DC Converter for Fast Transient Load-on-Demand* describes a power management IC (PMIC) or on-die regulator that supplies power to a compute domain. When the compute domain suddenly consumes more power (e.g., during a burst of computation), the voltage droops. A fast regulator can respond within nanoseconds, preventing timing violations. This requires careful analog circuit design, compensation networks, and integration with digital control.

### Physical Design and Layout Optimization
Once RTL is complete, physical design—placement and routing—optimizes for area, power, and timing. This is increasingly automated but still requires deep expertise.

#### Interconnect Optimization
Wires are expensive: routing a signal across a chip consumes significant power (especially in long global wires) and area. *Power grid optimization for high-frequency datapaths* focuses on power delivery: the wires that supply voltage and ground must be thick enough that the voltage drop is acceptable (typically < 3% of supply). In a high-frequency design with rapidly switching datapaths, voltage drop can cause timing failures. Optimization involves choosing which layers to use for power routing, placing power vias efficiently, and balancing power distribution across the die.

#### Placement and Clustering
Physical design tools place logic cells (gates, registers) on the die to minimize wirelength, which correlates with power and timing. Optimal placement is NP-hard; tools use heuristics (simulated annealing, genetic algorithms). Recent papers apply ML to predict good placements faster than traditional tools, reducing design time from weeks to days.

#### Clock and Timing Closure
A large die (> 50 mm^2) cannot have a single clock; clocks must be distributed carefully to minimize skew (the time difference between clock arrival at different points). *A Low-Power, Low-Noise, High-Performance Re-Convergent Clock Mesh Design for Large AI Compute Clusters* describes a clock mesh optimized for AI accelerators: it provides low skew (tight timing) while minimizing power. Clock power can be 20–30% of total power, so optimization here is critical.

### Emerging Technologies and Beyond-CMOS Computing
As CMOS scaling slows, researchers explore alternative technologies: quantum computing, memristive computing, spintronic memory, and wide-bandgap semiconductors.

#### Quantum Error Mitigation and Hybrid Systems
Quantum processors (noisy intermediate-scale quantum, or NISQ) are error-prone: two-qubit gates fail 1–5% of the time. *Quantum Analysis of LESCA* and other papers explore hybrid classical-quantum systems where classical circuits handle error correction and verification. The classical hardware must interface with quantum devices, manage error correction overhead, and orchestrate computation. This is speculative work—practical quantum advantage is years away—but the hardware design problems are real.

#### Memristor and ReRAM-Based Computing
Memristors—devices whose resistance depends on history—can perform computation and storage simultaneously. A memristor array can act as both memory and arithmetic unit. Papers explore using memristors for in-memory computing, particularly for approximate applications. The challenges are: memristor models are imperfect, variability is high, and cycling endurance is limited (a memristor wears out after 10^10 writes).

#### Spintronic Devices and Magnetic Tunnel Junctions
*Tunnel Magnetoresistance in Strained L10-FeAu Perpendicular Magnetic Tunnel Junction* explores magnetic tunnel junctions (MTJs)—devices where resistance depends on relative magnetic orientation—as non-volatile memory and computational elements. MTJs don't leak current (unlike CMOS) and can be fast and dense. The challenge is integrating MTJs with CMOS for control and sensing.

#### Wide-Bandgap Semiconductors
Traditional CMOS uses silicon. Wide-bandgap (WBG) semiconductors like GaN and SiC have larger bandgaps, allowing higher operating temperatures, higher voltages, and lower leakage. *Physical Insights into the Leakage Mechanisms Governing the Scaling Trends in 4H-SiC Based Junctionless FETs* investigates device physics for SiC, aiming to understand and mitigate leakage. WBG devices are crucial for power electronics (converters, motor drives) but are less mature for high-frequency logic than CMOS.

### Memory Systems and Architecture
Memory—SRAM, DRAM, Flash—dominates modern chip area and power. Designing memory subsystems that balance capacity, bandwidth, latency, and efficiency is an unsolved problem.

#### Memory Reliability and Variability
Process variation affects memory cells more than logic: a DRAM cell's capacitance can vary by 20%, causing read failures or data retention problems. *Memory_reliability_and_variability* papers focus on understanding and mitigating these effects through circuit design (self-timed sensing, improved cell designs) or system-level techniques (ECC, adaptive refresh rates for DRAM).

#### High-Bandwidth Memory
AI accelerators and datacenters need bandwidth: > 500 GB/s for modern accelerators. This requires either wider memory buses (more pins, higher cost) or higher clock rates (dissipates more power). High-Bandwidth Memory (HBM) stacks multiple DRAM layers and connects them with thousands of through-silicon vias (TSVs). Papers in this area focus on optimizing TSV design, managing thermal effects of stacked memory, and routing in 3D layouts.

#### Memory-Centric System Design
Some papers propose systems where memory (not CPU) is the focus: instead of moving data to compute, move compute to memory. This requires integrating processing capability into memory arrays—compute-in-memory—or changing system architecture to reduce data movement.

### Analog and Mixed-Signal Circuit Design
Analog design—designing circuits that handle continuous signals rather than discrete bits—is increasingly relevant as chips integrate sensors, power management, RF, and signal processing.

#### RF and Millimeter-Wave Circuits
Radio frequency (RF) and millimeter-wave (mmW) circuits operate at gigahertz frequencies and require careful attention to signal integrity, noise, and impedance matching. *N-Well Patterning of P-Type CMOS Substrate for Improving Quality Factor of on-Chip Inductors at Millimeter Wave Frequencies* describes how substrate design affects on-chip inductor quality—a key component in RF circuits. At mmW frequencies (28–73 GHz), parasitic capacitance becomes dominant; the paper shows how substrate structure can reduce these parasitic effects.

#### Signal Processing and Sensor Interfaces
Edge devices integrate analog sensors (accelerometers, temperature sensors, microphones) and need analog-to-digital converters (ADCs) and signal processing. Low-power audio processing is particularly relevant: smart speakers, hearables, and voice assistants require always-on audio detection. *A 0.75mm2 407μW Real-Time Speech Audio Denoiser with Quantized Cascaded Redundant Convolutions* implements a neural network-based audio denoiser that runs continuously on a wearable, processing microphone data in real-time while consuming < 0.5 mW.

#### Power Management and Voltage Regulation
On-die voltage regulators must supply multiple domains at different voltages with high efficiency. Traditional off-chip regulators are bulky and slow; on-die regulators are compact but must dissipate heat carefully. Papers explore switched-capacitor converters (efficient but fixed ratio), inductor-based buck converters (flexible but bulky), and hybrid approaches.

### Specialized Applications and Domain-Specific Accelerators
Several papers describe hardware for specific applications: genomics, digital microfluidics, health monitoring, and security.

#### Genomic Accelerators
DNA sequence matching (e.g., Smith-Waterman alignment) is compute-intensive and important for genomics. *Specialized accelerators for computational biology* describe hardware that exploits the regular structure of alignment algorithms to accelerate them 100–1000× compared to CPUs.

#### Digital Microfluidic Biochips
Digital microfluidics manipulates droplets of reagents on a chip for chemistry and biology lab-on-chip applications. *Enhancing Digital Microfluidic Biochip Operations with Scheduling Interval Method* optimizes the control logic that orchestrates droplet movements, reducing latency and power.

#### Wearable and Health Monitoring
Wearable sensors (ECG, EMG, temperature) generate data continuously. Local processing reduces power: transmitting 1 MB of sensor data wirelessly costs ~1 J, while processing 1 MB of data locally costs ~10 mJ. *Embedded mmwave signal processing for health monitoring* describes hardware for processing radar data to detect cardiac parameters (heart rate variability, respiration rate), enabling always-on health monitoring without battery drain.

### Design Automation and AI-Assisted EDA
The final major category comprises tools and automation for hardware design itself: how to design faster, cheaper, and more reliably.

#### Machine Learning for Design Space Exploration
AI accelerators have vast design spaces: datapath width, memory hierarchy, interconnect topology, clock frequency. Exploring all combinations is infeasible. ML models trained on prior designs can predict performance, power, and area for unseen configurations, enabling faster design-space exploration. *Boosting System-on-Chip Performance Through AI-Assisted Optimization Using Compositional Neural Networks* uses graph neural networks to represent circuit structure and predict performance.

#### ML for Physical Design
*Physical Synthesis Optimization Prediction Using Machine Learning* and *ML-based optimization for physical design* apply ML to placement, routing, and timing closure—traditionally handled by heuristic EDA tools. The insight is that these problems have structure: placements that group related logic together tend to be good. ML can learn these patterns and generate better solutions than traditional heuristics.

#### Formal Verification Acceleration
*ML-guided formal verification* combines ML with formal verification: use ML to guide the state space exploration toward likely bugs, then use formal methods to prove properties rigorously. This combines the efficiency of ML with the rigor of formal methods.

### Cross-Cutting Patterns

Several themes emerge across multiple subthemes:

**Precision-Efficiency Tradeoffs**: Approximate computing, quantization, and low-precision arithmetic appear in ML acceleration, neuromorphic computing, and low-power design. The fundamental insight is that perfect precision is expensive; accepting small errors unlocks dramatic efficiency gains.

**Parallelism and Communication**: Whether designing an SNN accelerator, a crypto engine, or a GPU, the challenge is balancing parallelism (doing many operations simultaneously for throughput) with communication (moving data between parallel units costs energy and latency). Specialized interconnects (meshes, trees, ring networks) are often better than general-purpose buses.

**Verification at Multiple Scales**: Correctness is ensured through simulation (fast but incomplete), formal methods (complete but expensive), and post-silicon testing (real but expensive). No single technique suffices; practical designs use all three.

**Power Optimization as Co-Design**: Reducing power is not just circuit design or architecture; it requires rethinking the algorithm, the dataflow, the memory hierarchy, and the physical layout together. Single-layer optimizations (e.g., better transistor layout) yield 10–30% improvements; multi-layer co-design yields 2–5× improvements.

**Heterogeneity**: Monolithic designs (all cores identical) are simpler but inefficient. Heterogeneous designs use small cores for sequential code and large cores for parallel code, specialized accelerators for specific workloads, and different voltage domains for different workloads. This complexity is justified by 2–4× better efficiency.

## How VLSID fits in the ecosystem

VLSID occupies a critical role in the semiconductor design ecosystem, bridging research and practice. The conference is upstream of EDA tools and downstream of semiconductor research, providing a venue where emerging technologies become implementable designs and where design problems drive new research directions.

### Relationship to Architecture and Algorithm Venues
Architecture conferences (ISCA, ASPLOS) focus on ISA design, processor microarchitecture, and system-level optimization. They assume working hardware and ask "how do we organize computation?" VLSID assumes a specific computation (say, matrix multiply) and asks "how do we implement it in silicon?" The division of labor is productive: architecture explores solutions at high abstraction, VLSID validates feasibility and describes tradeoffs at implementation level.

### Relationship to EDA and Physical Design
EDA tool developers (Cadence, Synopsys, Siemens) build tools used by every VLSID-track designer. These tools (synthesis, place-and-route, formal verification) are complex, proprietary, and expensive. VLSID papers often critique tool limitations and propose workarounds or new algorithms that should be incorporated into tools. For example, papers on ML-accelerated placement suggest that next-generation tools should use ML-guided optimization. Tool vendors monitor VLSID closely for insights into future design needs.

### Relationship to Manufacturing
VLSID designers work closely with foundries (TSMC, Samsung, Intel) to understand technology capabilities and limitations. As technologies scale to 3 nm and below, process variation becomes severe, yield drops, and design-for-manufacturability (DFM) becomes essential. Papers on process variation, reliability, and circuit techniques for advanced nodes inform both designers and foundries about what works in practice.

### Relationship to Emerging Device Research
As CMOS scaling slows, exploratory research on beyond-CMOS technologies (quantum, memristor, photonic) accelerates. VLSID papers on these technologies translate research concepts into circuit designs and evaluations. This feedback loop is crucial: device researchers can optimize for what designers need, and designers can provide realistic estimates of design complexity and benefit.

## What is not yet solved

VLSID 2025 highlights open problems that define the field's frontier:

**Verification Remains Intractable**: The gap between simulation capacity and design complexity grows. A 100M-transistor chip has 2^100M potential states; simulation explores perhaps 2^30. Formal verification tools can handle only small designs (< 1M transistors). Post-silicon bugs are common, delaying products and requiring costly re-spins. The field lacks a scalable, practical verification methodology that provides high confidence without exponential cost.

**Power Optimization is Ad-Hoc**: Despite 30 years of research, reducing power requires manual expertise and domain knowledge. A designer must simultaneously optimize architecture (dataflow, memory hierarchy), circuits (transistor sizing, voltage assignment), layout (floorplanning, routing), and algorithms (quantization, sparsity). Coordinating these across design hierarchies is error-prone. Automation here—a "power optimizer" tool that takes RTL and produces optimized silicon—remains out of reach.

**Design Complexity Outpaces Tools**: The latest NVIDIA GPUs have 80–100 billion transistors and took 5+ years and teams of > 1000 engineers to design. The design process is inherently expensive, limiting who can build accelerators. Academic teams and startups struggle to compete because tool cost, design cost, and manufacturing cost are all high. Making hardware design more accessible—better tools, open-source IPs, and faster design cycles—is an open challenge.

**Memory Bandwidth Scales Slower than Compute**: AI accelerators have grown 100× more powerful in 10 years, but memory bandwidth has grown only 10×. The consequence: accelerators are compute-bound (stalled, waiting for data), not fully utilized. Solving this requires architectural innovation (more on-chip memory, hierarchical computation, sparsity) and manufacturing innovation (higher bandwidth memory, 3D integration). Papers in VLSID hint at solutions but no breakthrough technology has emerged.

**Reliability in Advanced Nodes**: Process variation, circuit aging, and radiation effects make 3 nm silicon inherently less reliable than 65 nm silicon. Yet 3 nm must support more complex algorithms with no room for failures. Current solutions (ECC, redundancy) add 5–20% overhead but become unfeasible at 1 nm. The field lacks a scalable reliability solution that works at high process variation and high density.

**Security Hardware is Expensive**: Mitigating side-channel attacks, preventing IP cloning, and protecting against fault injection all add cost (area, power) with no algorithmic benefit. A fully hardened AI accelerator might be 30% larger and 20% slower than an unsecured baseline. The field lacks efficient security primitives, forcing a choice between security and efficiency.

**Neuromorphic Hardware Lacks the Killer App**: Neuromorphic processors promise 100× efficiency over conventional processors for spiking neural networks, but SNNs themselves remain less accurate and less understood than ANNs. Until SNNs match ANN accuracy on standard benchmarks, adoption will be limited. This is a chicken-and-egg problem: neuromorphic hardware investment is low because SNNs are immature, but SNN research is limited because hardware access is scarce.

**Quantum Error Correction Requires Massive Overhead**: To run useful quantum algorithms, quantum computers must correct errors. Current approaches require ~1000 physical qubits per logical qubit. No one knows how to build quantum computers at this scale, and the classical hardware required to manage error correction is enormous. The path from current 100–1000 qubit systems to useful quantum computers is unclear.

**Analog Design Remains a Bottleneck**: As mixed-signal chips integrate more functionality (RF, analog signal processing, power management), analog design becomes a critical path. Yet analog design is more difficult than digital: no perfect CAD tools, more sensitivity to process variation, and harder to verify. Analog designers are in short supply, limiting how much analog can be integrated. Better tools and methodology for analog design are needed.

**Emerging Technologies Have Limited Maturity**: Memristors, spintronic devices, photonic components, and other beyond-CMOS technologies are promising but immature. Variability is high, manufacturing is unreliable, and design tools don't exist. Transitioning these from lab demonstrations to manufacturable products remains speculative.

In synthesis, VLSID 2025 captures a field at a pivot point. The easy gains from scaling are exhausted; future progress requires deeper co-design of algorithms, architecture, circuits, and layout. The conference's diversity—spanning from ultra-low-power IoT to exascale training accelerators, from quantum computing to neuromorphic systems—reflects the breadth of this challenge. No single design methodology will suffice for all contexts; instead, designers must cultivate deep expertise in specific domains and understand the precise constraints that define those domains.

