# ICCAD 2025 — Computer-Aided Design at the Intersection of Everything

## What ICCAD Is

The International Conference on Computer-Aided Design is where the hardware design abstraction stack hits physical reality. While DAC (Design Automation Conference) casts a broader net across the entire semiconductor business, ICCAD is where researchers publish the algorithms and tools that close the gap between "here's what I want to build" and "here's what the foundry can actually manufacture."

ICCAD accepts ~280–300 papers annually from a field of 1000+ submissions. The acceptance rate has tightened in recent years, making it increasingly selective. The conference reflects the intellectual interests of VLSI researchers at semiconductor companies (Intel, Apple, Nvidia, Samsung, TSMC's research groups), EDA vendors (Cadence, Synopsys, Siemens), and academia (Berkeley, MIT, UT Austin, CMU, CalTech). Publication there signals that an idea solves a real bottleneck, not a hypothetical one.

What defines ICCAD's scope is neither a specific tool nor a narrowly bounded domain, but a philosophical commitment: **the conference assumes that manufacturing constraints are non-negotiable, and therefore the art of design is the art of respecting them**. Physical design must close timing, handle power delivery, avoid lithographic hotspots. RTL must map to gates that a place-and-route tool can actually implement. Analog circuits must tolerate process variation. Memory systems must trade capacity, latency, and power under hard physical limits. This is why ICCAD papers rarely discuss architecture in isolation—they discuss architecture *in tension with what silicon can deliver*.

## The One Problem This Community Is Organized Around

ICCAD researchers are solving a single, decades-old problem: **the design-closure problem**.

When a chip designer specifies a circuit, they operate in abstraction. An architect says "I want a 512-bit FP64 multiply unit with single-cycle latency." A logic designer synthesizes this to gates and flip-flops. But those gates must fit on silicon. They must be placed such that wires connecting them don't exceed timing budgets. Power must flow through metal layers without creating electromigration hazards. Clock signals must reach every register within ±100ps. Heat must dissipate without exceeding junction temperature limits.

At the 14 nm node, these constraints were tight but manageable. Today at 3 nm (and the roadmap beyond), they are actively hostile.

**Why the design-closure problem got worse:**

1. **Shrinking feature sizes increase sensitivity to everything.** At 65 nm, a 1% variation in wire resistance was noise. At 3 nm, it dominates the timing path. At 1.4 nm (Intel 18A), parasitic cross-coupling between wires causes propagation delays to vary by 15% depending on neighboring wire patterns. The design must anticipate these effects before the design exists.

2. **3D integration traded planar area for vertical complexity.** A wafer-scale chip or a chiplet array eliminates the 2D plane as the bottleneck—now thermal gradients, power delivery through TSVs (through-silicon vias), and inter-chiplet latency become the binding constraints. Physical design must optimize across three dimensions, not two. A chiplet placement that looks good in 2D might create a thermal hotspot in the third dimension, stalling clocks and breaking timing on unrelated parts of the chip.

3. **Heterogeneous design became the default.** A modern SoC is not a homogeneous sea of logic gates. It contains analog blocks (PLLs, voltage regulators, sensor interfaces), mixed-signal blocks (ADC/DACs for RF), memory macros (SRAM, HBM, emerging memory), specialized compute (vector units, matrix engines), and hard IPs (PCIe, Ethernet). Each subsystem has radically different design rules. SRAM timing depends on bit-line coupling; memory compiler output is non-portable across foundries. Analog circuits are hand-crafted for each process corner and require simulation at the circuit level, which doesn't scale to 100M+ transistor systems. The closure loop must coordinate across these heterogeneous domains.

4. **Manual design stopped scaling.** A 1990s chip like the Pentium was designed by teams of 100–200 humans over 3–5 years. A modern GPU has 50,000–100,000+ transistors per "design team member," meaning the human labor per unit transistor has dropped 10,000x. If designers were still manually placing cells and routing wires, we'd still be at the 28 nm node. The only way forward is automation. But automation requires encoding the design rules, optimization objectives, and physical constraints into algorithms—and those algorithms have become the entire field of computer-aided design.

ICCAD 2025 is fundamentally about **automating the closure loop**—the iterative process of: (1) propose a design, (2) check whether it violates physical constraints, (3) perturb the design to relax violations, (4) repeat. The difference between a tapeout that works and one that fails in silicon is often a few micrometers of routing, a 50 mV drop in power delivery, or a handful of timing paths meeting delay by less than 5%. ICCAD papers are about the algorithms that find those margins.

---

## ML-for-EDA: Learnable Closure

The first radical shift at ICCAD 2025 is the migration of design decisions from hand-coded algorithms to neural networks trained on historical designs.

**Why ML enters EDA now:** Traditional algorithmic approaches to design automation are *greedy*. A timing-driven placer uses a greedy partitioning or simulated-annealing heuristic to place cells, then evaluates the result against a timing calculator. This works well for incremental improvements but poorly for radical reconfigurations. A routing tool uses graph search with heuristics to route each net, but the order in which nets are routed (the "order dependency") creates a combinatorial trap: route net A before net B, and B has no valid path; reverse the order, and A blocks B. The global optimum lies in a configuration space so large that no algorithm can exhaustively search it.

Machine learning sidesteps this by learning from data: "Given the designs that succeeded, what features predict which placement will close timing?" This is the insight behind **ML-for-EDA papers** at ICCAD 2025. The high-profile examples are:

- **DecoRTL** (syntax-aware LLM decoding for RTL generation): Rather than training a vanilla neural network to generate Verilog token-by-token, DecoRTL incorporates the Verilog grammar into the decoding process. At each step, the model is constrained to only propose tokens that produce syntactically valid code. This works because RTL generation has structure—a module declaration must contain only valid constructs—and neural networks are weak at learning syntax. By baking syntax into the model, fewer parameters are wasted on learning "don't put a semicolon there," and more capacity remains for learning semantics ("for this logic function, this RTL pattern is more synthesizable").

- **AnaFlow** (agentic LLM for analog design): Analog design is the most manual part of chip design. A circuit designer for an amplifier must iterate: choose a topology, solve for component values, simulate transient response, check noise, adjust biasing, simulate mismatch under process corners. This loop is inherently sequential—later decisions depend on earlier ones—and requires deep domain knowledge. AnaFlow models this as an agent with a reasoning loop: the LLM proposes a design step, calls a simulator to evaluate it, reasons about the results, and decides the next action. This is powerful because it defers to the simulator (ground truth) rather than hallucinating outcomes, and it lets the LLM focus on the "thinking" part of design rather than the "memorization" part.

**Why this works at scale:** ML-for-EDA papers rarely claim to replace human designers. Instead, they replace the *expensive inner loop*—the one that runs millions of times during optimization. A timing prediction model might take 1 ms and use 100x less compute than a full SPICE simulation. A placement prediction model might evaluate millions of candidate placements in the time it takes a simulator to evaluate one. By making the inner loop faster and learnable, the outer loop (human guidance, constraint specification, convergence checking) can remain in the human domain.

The risk, acknowledged in the ICCAD community but not yet solved, is **generalization**: Does an LLM trained on analog designs at TSMC 5nm generalize to Samsung 3nm? Does a graph neural network trained to predict timing on a CPU design work for a GPU? The papers show strong results on held-out test sets from the same foundry/design family, but cross-domain evaluation is rare. This is ICCAD 2025's open frontier in ML-for-EDA.

---

## Physical Design Under 3D Constraint

The second dominant theme is **3D integration**, but this term obscures the real problem: the vertical axis has become a design dimension.

**Why 3D integration exists:** The planar density of modern chips—transistors per mm²—has plateaued. 3 nm technology offers ~150–300 million transistors per mm², and the next node offers maybe 2x more. Meanwhile, chip complexity demands more transistors: a modern GPU has 50 billion transistors; an AI training accelerator demands 100+ billion. Fitting this onto a single wafer in 2D requires impossibly large die (>600 mm², hitting reticle limits and yield cliffs). 3D integration—stacking dies on top of each other—provides a new axis of integration.

But this trade-off is not free. Stacking dies introduces new constraints:

1. **Power delivery becomes three-dimensional.** In a 2D chip, power delivery is a network of metal layers above the transistors. In a 3D stack, current must flow vertically through TSVs (thin tubes of metal through the silicon), and each TSV has limited current capacity. A poorly placed TSV might become a bottleneck for an entire layer of the stack. Worse, the resistance of a TSV changes the effective impedance of the power delivery network, creating resonances that weren't present in 2D designs.

2. **Thermal stacking is a tightly coupled problem.** Heat flows vertically through the stack. If layer 0 (the base die) has a 100W hotspot, and layer 3 is stacked directly above it, the temperature at layer 3 increases by 20–50°C relative to layer 1 due to conduction through the intermediate layers and encapsulant. Clock frequency and leakage power are both strongly temperature-sensitive (frequency drops ~300 MHz per 10°C; leakage can double over a 40°C range). A hotspot in layer 0 can cause layer 3 to throttle even if layer 3 itself is cool. **NSTherm** (error-bounded thermal simulator for 3D stacks) at ICCAD 2025 addresses this by building a thermal model that respects the 3D heat flow and iteratively tightens error bounds. This matters because naive 2D thermal simulators predict layer 3 will be 10–15°C cooler than layer 0, but the actual difference is 50–80°C in stacked designs; design decisions optimized with the wrong model fail in silicon.

3. **Chiplet placement becomes a partitioning problem with locality constraints.** A monolithic GPU might have compute cores spread uniformly across the die and connected via a 2D NoC. A chiplet-based GPU must partition compute cores into separate dies (chiplets), then place chiplets to minimize inter-chiplet latency and power. Chiplet A (compute) must be close to chiplet B (L3 cache), but far from chiplet C (I/O). But "close" in a 3D stack is not just X-Y distance—it's also Z (which layer?) and TSV density (are enough TSVs available in this region?). The search space grows exponentially: not only *which* cells go in *which* chiplet, but *which* chiplet goes in *which* layer. ICCAD 2025 papers on 3D placement use partition-aware algorithms, machine learning for chiplet-to-layer assignment, and constraint solvers to jointly optimize partitioning and placement.

**AccelStack** (cost analysis of 3D-stacked LLM accelerators) exemplifies this problem. Training a large language model requires massive matrix multiplies, which are best accelerated with spatial computing (systolic arrays or spatial dataflow). A single-layer accelerator fast enough for LLM training would be ~400–600 mm² (hitting reticle limits). Stacking three layers of smaller accelerators avoids reticle constraints but introduces 3D design challenges: thermal management (top layers run hotter), power delivery (TSV capacity), and inter-layer communication (chiplet-to-chiplet handoff). AccelStack quantifies the trade-offs: three-layer stacks reduce area by 30% but increase latency by 8–12% and power by 15% due to thermal throttling and inter-layer communication overhead. The paper's value is that it forces the designer to make this trade-off consciously, not by accident.

---

## Emerging Memory as Design Primitives

The third theme is **emerging memory technologies** (FeFET, MRAM, PCM, PIM) appearing not as "future replacements for DRAM" but as immediate, integrated parts of the design loop.

**Why emerging memory is different now:** For 30 years, memory technology was stable. A chip had SRAM (on-die caches, fast, high power, ~1-10 fJ per bit), DRAM (off-die, slow, lower power, ~10-100 fJ per bit), and maybe NOR flash for code. Designers could treat memory as a commodity: choose capacity and latency, synthesize an SRAM compiler, instantiate it, and move on. But DRAM and SRAM scaling have hit hard physical limits. DRAM cell size is approaching the limits of lithography. SRAM leakage power per cell has grown so large that 1 GB of on-die SRAM consumes 5–10% of total chip power even at idle.

Emerging memory technologies exploit different physics:

- **FeFET (ferroelectric FET)**: Uses a ferroelectric layer in the transistor gate to store charge without leakage. Can be embedded on-die with ~1–2 nm control gate thickness. Density approaches DRAM-like levels (but with SRAM-like leakage). The catch: FeFET switching is not instantaneous—write latency is 10–100 ns, compared to SRAM's <1 ns. Also, FeFET cells have limited write endurance (billions, not trillions, of cycles).

- **MRAM (spin-transfer torque MRAM)**: Uses magnetic tunneling junctions to store data. Non-volatile, high endurance, but density is lower than FeFET and access latency is ~10–50 ns.

- **PIM (processing-in-memory)** / **CIM (computing-in-memory)**: Embeds compute (adders, multipliers, or neural network-like operations) inside memory arrays, eliminating the data movement bottleneck.

These technologies are not ready to replace DRAM wholesale, but they are ready to be *specialized* for specific use cases. **FACAM** (FeFET-based analog CAM for efficient search operations) exemplifies this: a CAM (content-addressable memory) is a memory that searches for a value in parallel across all rows, returning the index of the match. Conventional CAMs use SRAM, which is power-hungry for parallel searches. FACAM redesigns the CAM using FeFET cells and analog search logic, reducing search power by 10x at the cost of introducing 5–10 ns latency. This is useful for systems that do frequent *associative searches* (like hashtable lookups in databases or ML inference) but not for systems that need sub-nanosecond latency.

**SPIMA** (sparse matrix via PIM-near processing) uses PIM to accelerate sparse matrix operations. Modern neural networks rely heavily on sparsity (many weights are zero, pruned away). A sparse matrix multiply on conventional CPUs/GPUs is slow because the compute-to-memory-traffic ratio is poor—you load many zeros that don't contribute to the result. SPIMA places simple arithmetic units inside the memory array, such that zero-valued entries are skipped without being loaded to main compute. This improves energy efficiency by 5–10x for sparse operations.

**Why this matters for ICCAD:** The presence of these specialized memories means the designer can no longer treat memory as a monolithic tier. Instead, they must *partition* data across heterogeneous memory technologies: hot data in FeFET (fast, low power), warm data in DRAM (higher latency, lower capacity), cold data in MRAM (non-volatile), and frequently-searched data in FACAM. This requires new optimization algorithms: data partitioning across memory types, placement of PIM units to minimize communication, and compilation of kernels to PIM-specific instruction sets. ICCAD 2025 papers on memory systems are solving these coupling problems, not designing the memories themselves.

---

## Security in Silicon

The fourth theme is **security attacks at the physical layer** and defenses that must be baked into the design.

**Why silicon-level security is now a design concern:** For decades, security was an application-level or system-level problem: encrypt data, authenticate code, isolate processes. But starting with Spectre/Meltdown (~2018), the security community realized that microarchitectural side channels—the timing of cache hits/misses, the patterns of memory access—leak secrets. And those side channels are *physical*, not logical. You cannot patch them with software updates; they require changes to hardware.

This spawned an arms race between attackers and defenders:

- **Rowhammer attacks**: DRAM cells are tiny capacitors that leak charge. Periodically, a DRAM controller must "refresh" each cell (recharge it). But if an attacker repeatedly accesses cells in adjacent rows, the refresh mechanism can be overwhelmed, causing a row to lose charge and flip bits. An attacker can exploit this to flip a single bit in a privilege bit-field, escalating from user to kernel. Defense: ECC (error-correcting codes) that can tolerate multiple bit flips, randomization of row addresses, or better isolation of the refresh mechanism. These are all low-level physical mechanisms—not software patches.

- **Speculative execution sidechannels**: Modern CPUs execute instructions speculatively (before confirming they're actually needed), then roll back if the speculation was wrong. But the speculative execution leaves traces in caches. An attacker can force speculation, observe cache timings, and infer secret values that were never supposed to be loaded into the cache. Defense: isolate caches, add noise to timing, or disable speculative execution (at performance cost). Again, this is a microarchitectural defense, not a software one.

- **Information flow tracking (IFT)**: Some papers track the flow of secret data through the hardware. If a bit loaded from a secret register is used to compute an address, that address is "tainted" as secret. If a tainted value is used in a timing-dependent operation (like a branch that affects execution time), the system flags a potential leak. IFT can be implemented at the hardware level (tag each value as secret/public) or the software level (instrument binaries to track taint). ICCAD papers focus on hardware-level IFT, which requires adding metadata planes to the processor (extra bits tracking taint state) and checking taint on every operation.

- **Post-quantum cryptography (PQC) hardware**: Quantum computers (if built) would break RSA and elliptic-curve cryptography. Post-quantum algorithms (lattice-based, multivariate, hash-based) have different computational patterns—more memory-intensive, different dataflows. Implementing PQC efficiently in hardware requires custom datapaths and memory hierarchies. ICCAD 2025 has papers on PQC accelerators, custom memory layouts for polynomial arithmetic, and area-optimized implementations targeting embedded systems.

The ICCAD 2025 security papers share a common insight: **security cannot be bolted on after the fact**. If you design a processor to optimize for latency and then add an IFT layer on top, the IFT tracking itself becomes a timing side-channel. If you add rowhammer defenses to an existing DRAM controller, you might break latency guarantees for other subsystems. Security must be *co-designed* with performance, power, and area from the start. This is why ICCAD researchers (who build the infrastructure upon which systems are built) are increasingly focused on security: it's a first-order design constraint, not a patch.

---

## Superconducting and Photonic Circuits

The fifth theme is **heterogeneous substrate technologies**: circuits that are not CMOS.

ICCAD 2025 includes papers on:

- **SFQ (Single Flux Quantum) superconducting circuits**: Use Josephson junctions (quantum devices) to represent bits. SFQ circuits operate at millikelvin temperatures and have zero static power dissipation (no leakage). They are inherently faster than CMOS (picosecond gate delays) and could theoretically scale to much denser packing. But SFQ circuits require exotic fabrication (niobium/titanium on silicon), cryogenic cooling (dilution refrigerators), and completely different CAD tools. ICCAD papers on SFQ focus on physical design for superconducting dies: routing optimization, timing analysis (propagation time through Josephson devices differs from CMOS gate delays), and thermal management (cryogenic systems have very limited cooling capacity, so power density must be low).

- **Photonic circuits**: Integrate photonic waveguides and modulators on silicon. Data is carried by photons instead of electrons, offering extremely high bandwidth and low power for communication (photonic links consume 10x less power than electrical links over long distances). But photonics are slow at computation—photonic adders are built from comparators, multiplexers, and filters, not logic gates. ICCAD papers on photonics focus on *optical network-on-chip* (NoC): mapping computation to electrical compute clusters and communication to photonic links, then designing the placement and routing of optical waveguides. This is a different layout problem than CMOS: waveguides must have specific bend radii (too tight, and light scatters), and thermal effects (temperature changes the wavelength of light, shifting filters out of band) require careful thermal management.

**Why these matter:** Both SFQ and photonic circuits are niche, unlikely to become the dominant compute paradigm. But they represent the expanding scope of ICCAD. The conference was founded to solve placement, routing, and timing for CMOS. Today it's solving those problems for *any* technology that needs it. This reflects a shift in the field: ICCAD is not "the CAD conference for CMOS"; it's "the CAD conference for *any* silicon technology."

---

## Formal Methods and Verification: Closing the RTL-to-GDS Gap

The sixth theme is **formal verification**: proving that a design meets its specification without simulation.

**Why formal verification matters more now:** Simulation is the traditional way to verify chips: write a testbench, simulate it, check that outputs are correct. But simulation covers a tiny fraction of the input space. A 64-bit adder has 2^128 possible inputs; no testbench can simulate all of them. As chips grow larger and more complex, simulation coverage has lagged. A modern GPU might have trillions of possible system states; simulating all of them is infeasible.

Formal verification sidesteps this by mathematically *proving* that the design satisfies a specification. For example:
- "This module always outputs the sum of its two inputs" (correctness)
- "This cache controller never allows two cores to simultaneously modify the same line" (coherence)
- "This finite state machine cannot reach an undefined state" (reachability)

Formal tools work by building a mathematical model of the circuit (usually a symbolic representation where wires are variables) and using decision procedures (SAT solvers, SMT solvers) to check whether the specification is satisfiable given the circuit's constraints. If not, the tool produces a counterexample—an input sequence that violates the spec—helping the designer debug.

**Formal verification in ICCAD 2025:** Papers span several approaches:

- **Formal verification of analog circuits**: Analog circuits are notoriously hard to verify because their behavior is continuous (not discrete like digital logic). A voltage regulator must maintain an output voltage within ±5% despite input voltage variations, load current changes, and process variation. Simulating all corners is possible but slow. Formal verification of analog systems uses SMT solvers and real arithmetic constraints. Papers at ICCAD 2025 show how to formally verify that a regulator meets its spec across all process corners and operating conditions.

- **Formal verification of EDA tools**: Even more meta: proving that a *place-and-route tool* doesn't introduce bugs. A router is supposed to connect nets without violating physical rules (no wires overlapping, design rules met). If the router has a bug, the output GDS is invalid, and the chip fails to manufacture. ICCAD papers formally verify key properties of routing tools: "This router never produces overlapping wires," "This router respects design rule minimum spacing."

- **Formal verification of hardware security properties**: Properties like "the output of this accelerator never depends on secret keys except through authorized channels" are hard to test but critical for security. Formal tools can check information-flow properties, proving that secret data doesn't leak through timing or cache side-channels.

The bottleneck in formal verification is *scalability*. Formally verifying a 10,000-gate design is feasible; verifying a multi-billion-gate GPU is not. ICCAD papers tackle this through *abstraction*—proving properties of small modules, then composing proofs to build up to the full chip—and through *incremental verification*—when a designer modifies a small part of a design, reusing previous proofs rather than re-verifying from scratch.

---

## What's Open: Genuine Unsolved Problems

Despite the advances reflected in ICCAD 2025, three major bottlenecks remain unsolved:

**1. ML-for-EDA generalization:** The papers show strong results on in-distribution test sets. But does a placement model trained on 7 nm CPU designs generalize to 3 nm GPU designs? To custom accelerators? To analog circuits? Early cross-domain evaluation suggests no. The ML community treats this as a transfer learning problem—can you fine-tune a model trained on CPU designs to work on GPUs? But the answer is unclear. Part of the problem is data scarcity: there are few publicly available large chip designs for training, and companies are reluctant to release their designs. Part is architectural mismatch: CPUs and GPUs have different structures (CPUs have deep pipelines, large caches; GPUs have many cores and on-chip memories), so design patterns that work for one don't apply to the other. Solving this would require either (a) much larger, more diverse training datasets, (b) better transfer learning techniques, or (c) models that explicitly encode domain knowledge about chip design, not just neural networks trained end-to-end.

**2. Analog circuit verification:** Digital circuits can be formally verified; analog circuits cannot (real arithmetic is undecidable). Simulating an analog circuit requires numerical integration of differential equations—slow and never exhaustive. Today, analog designers rely on simulation at multiple process corners and a lot of hand-checking. For complex analog circuits (on-die voltage regulators, phase-locked loops, sensor interfaces), the design cycle is 2–3x longer than digital because verification is expensive. ICCAD 2025 has papers on faster analog simulation and better corner selection (which process corners are most likely to fail?), but no solution to the fundamental problem: how do you *prove* an analog circuit works without simulating it?

**3. Thermal management in 3D stacks:** As stacks grow taller (3-4 layers now, 10+ layers projected), thermal gradients become severe. Layer 0 might be 50°C cooler than layer 3 (because heat flows through the stack). But clock frequency is temperature-dependent, so layer 3 must run at reduced frequency, reducing throughput. Today, designers manage this by (a) placing low-power workloads in the hot layers, (b) using thermal-aware placement to avoid hotspots, and (c) adding aggressive power throttling when temperatures exceed safe limits. But this is reactive and suboptimal. What's missing is *predictive thermal optimization*: given a workload, determine the optimal frequency scaling and task placement across layers *before runtime* such that the entire stack runs at maximum throughput while respecting thermal constraints. This requires coupling the performance model (how does frequency affect throughput?), the thermal model (how does power density affect layer temperature?), and the memory access pattern (which cores access which dies, affecting inter-layer traffic). Solving this jointly is an open problem.

---

## Conclusion: The Future of Design Closure

ICCAD 2025 reflects a field in transition. The old paradigm—humans specify designs, specialized algorithms optimize within narrow constraints (timing, power, area), tools produce GDS—is being replaced by a new one: humans specify high-level objectives, machine learning explores a vast design space, and tools integrate heterogeneous technologies (3D, emerging memory, photonics, SFQ) into a coherent whole.

But this transition is incomplete. ML-for-EDA works well for well-characterized problems (placement, routing, timing) where historical data is abundant and the objective is clear. It fails on novel problems (cross-domain generalization, analog design, security co-design) where data is sparse and the objective is nuanced.

The conference's core insight—that design closure is the hard problem, and everything else is detail—remains true. As feature sizes shrink, 3D integration deepens, and workloads diversify, the gap between what architects specify and what silicon can deliver grows wider. ICCAD researchers are building the tools to close that gap. Whether they're using simulated annealing, machine learning, formal verification, or human intuition, the mission is the same: **turn ideas into silicon, and do it fast enough that the next generation of chips can be designed before this one is obsolete**.
