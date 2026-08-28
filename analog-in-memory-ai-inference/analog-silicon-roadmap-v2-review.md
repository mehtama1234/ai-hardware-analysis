# Review: analog-silicon-roadmap-v2.pdf

Source file:

```text
/home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/analog-silicon-roadmap-v2.pdf
```

## Overall Read

The roadmap is directionally useful, but it is written too much like a confident investor pitch and not enough like an evidence-backed silicon execution plan.

The strongest idea is correct:

```text
Do not position analog IMC as a full replacement for NVIDIA, Qualcomm, or general digital AI chips.
Position it as a low-power physical-edge accelerator where analog compute, sensor proximity, and measured system energy can matter.
```

But several claims need to be softened, separated by evidence level, or converted into roadmap gates.

The document should become:

```text
Here is the opportunity.
Here is the chip hypothesis.
Here is what we can prove now.
Here is what is only supported by outside examples.
Here is what must be simulated.
Here is what must be measured on board.
Here is what must be proven before customer or investor claims.
```

## Major Findings

### 1. The Main Claim Is Too Broad

Current style:

```text
Building an unbeatable silicon and software stack.
```

Problem:

This is too strong. It sounds like the roadmap already proves dominance.

Better:

```text
Building an evidence-backed analog IMC silicon and software roadmap for selected Physical AI edge workloads.
```

Why:

Analog IMC may have a strong advantage in selected workloads, but not across all physical AI. The platform should prove fit case by case.

### 2. "Sub-Watt VLA Reflex" Needs Strong Boundaries

The document implies analog IMC can support low-power VLA inference and local tactile/DVS fusion.

Problem:

VLA workloads include hard digital parts:

- dynamic attention
- Softmax
- LayerNorm
- memory movement
- action head
- control timing
- safety logic

Analog may help with static matrix-heavy regions, but it does not automatically make the whole VLA workload sub-watt.

Better:

```text
Analog IMC may reduce energy for selected static matrix-heavy regions of Physical AI workloads. The platform must separately prove transformer partitioning, digital overhead, runtime, power, and task accuracy.
```

### 3. "Perfect Virtual Replica" Is Not Credible

Current style:

```text
Build a perfect virtual replica of our analog chip.
```

Problem:

Before silicon exists, the simulator is not perfect. It is a model with assumptions.

Better:

```text
Build a calibrated virtual chip model that starts with assumptions and improves as board and silicon measurements arrive.
```

Why:

This is exactly what our platform should enforce: simulator evidence is useful, but it is not measured hardware evidence.

### 4. AIHWKIT And CrossSim Should Not Be Treated As Full Chip Proof

The roadmap correctly names AIHWKIT and CrossSim, but it should say what each can and cannot prove.

AIHWKIT can support:

- analog noise risk
- drift risk
- ADC/DAC precision risk
- programming variation risk
- hardware-aware training experiments

AIHWKIT cannot prove:

- board runtime
- board power
- packaged-chip thermal behavior
- production silicon behavior
- compiler readiness

CrossSim can support:

- crossbar layout risk
- wire/parasitic risk
- bit-slicing risk
- ADC range risk
- programming/read-noise risk

CrossSim cannot prove:

- full system runtime
- final board power
- final task accuracy by itself
- production readiness

### 5. The Roadmap Collapses Too Many Hard Problems Into 36 Months

The roadmap includes:

- simulator
- PyTorch/JAX integration
- analog-mlir compiler
- hybrid chiplet
- STT-MRAM or FeRAM transition
- Isaac Sim integration
- HIL testing
- FPGA safety controller integration
- 300mm fab scaling

Problem:

That is too much to present as one smooth three-year path.

Better:

Convert it into proof gates:

```text
Gate 1: useful simulator and model-fit workflow
Gate 2: compiler mapping and analog/digital split
Gate 3: board runtime and power proof
Gate 4: task accuracy proof
Gate 5: update/reliability proof
Gate 6: packaging/foundry proof
```

### 6. STT-MRAM / FeRAM Recommendation Is Too Definite

Current style:

```text
Transition to STT-MRAM or FeRAM.
```

Problem:

This assumes those memories solve the update problem. They may help with endurance or write behavior, but the chip still needs evidence for:

- analog precision
- multi-level storage behavior
- write energy
- write latency
- endurance
- retention
- variability
- integration cost
- area
- foundry availability

Better:

```text
Evaluate memory technologies for update-capable analog inference. STT-MRAM, FeRAM, RRAM, PCM, and other options should be compared against write energy, write latency, endurance, retention, precision, variability, and foundry path.
```

### 7. Extreme Technical Solutions Need Evidence Boundaries

The PDF mentions:

- triple-well isolation
- glass package
- leaf-vein cooling channels
- Group-Level Parallelism
- analog 4-bit filtering block
- 75 percent data pruning
- 5.74x speedup
- 76 percent temperature reduction

Problem:

Some of these may be valid as research-inspired examples, but the document presents them as our planned solution before the chip architecture has selected them.

Better:

Use them as candidate design patterns:

```text
Candidate mitigation: triple-well isolation, guard rings, floorplan separation, package isolation, or glass substrate depending on process and package constraints.
```

```text
Candidate thermal mitigation: floorplan changes, heat spreading, package choice, thermal vias, liquid cooling, or advanced channel designs depending on power density and market.
```

```text
Candidate scheduling mitigation: ADC sharing analysis, tile scheduling, column grouping, or Group-Level Parallelism if the physical architecture requires it.
```

### 8. The Competitive Matrix Is Useful But Needs Safer Language

The table is useful because it separates:

- central SoCs
- reflex controllers
- analog IMC

But "unassailable physical advantage" is too strong.

Better:

```text
Analog IMC target advantage: low-power matrix-heavy inference close to sensors, if compiler mapping, digital overhead, board power, and task accuracy are proven.
```

### 9. Missing: Clear Customer Entry Point

The PDF talks about strategy, but it does not show how a customer starts.

Our platform should add:

```text
Customer brings model + workload + success target.
Platform shows analog fit, proof, blockers, and next pilot requirements.
```

### 10. Missing: What Must Be Measured

The roadmap should explicitly require:

- model-level analog simulation
- crossbar simulation
- compiler mapping
- full-system runtime simulation
- board latency
- board jitter
- power trace
- thermal trace
- task accuracy
- calibration stability
- weight update energy
- write endurance
- rollback behavior
- sensor path latency and energy

Without these, the roadmap reads as a claim list rather than an execution plan.

## Recommended Rewrite Structure

### 1. Positioning

```text
Analog IMC is not a general replacement for digital AI silicon.
It is a candidate accelerator for selected physical-edge workloads where matrix-heavy inference, sensor proximity, low power, and local latency matter.
```

### 2. Product Thesis

```text
The product is a chip plus a proof workflow.
Customers and investors will not buy "analog is efficient."
They need proof that their workload maps, runs, saves energy, keeps accuracy, and has a safe claim boundary.
```

### 3. Three Build Pillars

```text
Virtual chip model:
simulate analog behavior before silicon, then calibrate with measurements.

Hybrid chip:
analog for matrix-heavy static work, digital for dynamic attention, control, safety, and runtime logic.

Zero-touch translator:
compiler/runtime path that turns normal model formats into analog/digital execution plans.
```

### 4. Six Roadmap Gates

```text
Gate 1: Model and analog fit
Gate 2: Analog and crossbar simulation
Gate 3: Compiler mapping
Gate 4: Full-system runtime
Gate 5: Board, power, thermal, and task proof
Gate 6: Reliability, updates, packaging, and production path
```

### 5. Claim Discipline

```text
Simulator output supports simulation claims.
Compiler mapping supports compiler claims.
Board runtime supports latency claims.
Power traces support power claims.
Task tests support task claims.
Reliability tests support lifetime/update claims.
```

## How This Should Feed Our Platform

The PDF should become a roadmap input, not the final product story.

Our platform should convert its claims into 14 journey steps:

1. Model Intake
2. Analog Fit
3. Analog Accuracy Risk
4. Crossbar Layout Risk
5. Hardware Cost Estimate
6. Compiler Mapping
7. Transformer And VLA Check
8. Full-System Runtime
9. Board Runtime
10. Power And Thermal
11. Task Accuracy
12. Weight Update Readiness
13. Sensor To Model Path
14. Final Answer

Each PDF claim should be mapped to:

- the journey step it belongs to
- the evidence required
- the toolkit that can help
- the claim it can support
- the claim it cannot support
- the next measurement or build step

## Practical Action Items

1. Replace "unbeatable" and "unassailable" with evidence-backed language.
2. Replace "perfect virtual replica" with "calibrated virtual chip model."
3. Separate analog matrix advantage from full VLA system readiness.
4. Treat STT-MRAM and FeRAM as candidates, not decisions.
5. Treat glass packaging, leaf-vein cooling, GLP, and analog pruning as candidate mitigations until architecture evidence exists.
6. Add a proof-gate table for every major claim.
7. Add a measured-evidence checklist.
8. Add a customer journey: model upload to final safe claim.
9. Add investor journey: thesis to proof gaps to funding milestones.
10. Add engineering journey: blocked claims to work orders.

## Bottom Line

The roadmap has the right ambition and several useful technical directions.

It needs to become more evidence-based.

The strongest version is:

```text
We are building a hybrid analog IMC platform for selected physical-edge workloads.
We will prove the fit through a simulator, compiler, board, power, task, update, and sensor evidence workflow.
Every claim will be tied to the proof source that supports it.
Anything not proven stays blocked.
```

