# Simulation-To-Silicon First-Principles Specification

## Purpose

This document defines the end-to-end product we are building around Analog In-Memory Computing (AIMC), Physical AI, and transformer/VLA-era workloads.

The goal is not to build a generic dashboard and not to repeat the claim that "analog is efficient." The goal is to build an evidence-backed workbench that can answer:

```text
Can this model and physical-world workload move through a credible simulation-to-silicon path for this analog chip, and what evidence proves or blocks each claim?
```

The platform should bring together model analysis, hardware-aware simulation, crossbar accuracy modeling, compiler placement, system simulation, board/runtime measurement, power/thermal evidence, task accuracy, and safe claim generation.

The output is a roadmap-grade package for founders, ML engineers, hardware engineers, customers, and investors.

## Central Product Question

The end-to-end platform exists to answer one customer-facing question:

```text
Can this workload credibly run on this analog chip, what proof exists, what breaks, and what must be built or measured next?
```

The platform should answer this as a connected workflow, not as separate tool reports.

### What The Platform Must Do For The User

For every workload package, the platform must produce five concrete answers:

1. Fit: whether the model and Physical AI workload match the analog chip's strengths.
2. Proof: which evidence exists today, including model analysis, simulation, compiler placement, board runtime, power/thermal data, and task accuracy.
3. Breaks: which operators, system boundaries, toolkit gaps, physics effects, update paths, or evidence gaps block stronger claims.
4. Next work: what must be built, connected, simulated, measured, rewritten, or imported next.
5. Safe claim: what the team can say to a customer, investor, or internal roadmap review without overstating the evidence.

The user's visible output should look like:

```text
Workload: warehouse robot tactile-camera policy
Analog fit: partial
Proof today: ONNX graph analysis, source-checked toolkit plan, local estimate
Breaks: dynamic attention, missing CrossSim sweep, missing compiler placement, no board power trace
Next work: run CrossSim parasitic sweep, import analog-mlir placement, measure write/update energy
Safe claim: analog-friendly projection and MLP regions identified; adaptive VLA readiness is not proven
```

### Platform-Owned Capabilities

These are capabilities our product must own directly, even when external toolkits provide part of the evidence:

- workload intake: accept a model, target domain, modality, deployment profile, and chip assumptions
- operator analysis: identify analog-friendly layers, digital-required operators, unsupported regions, fallback regions, and graph rewrite candidates
- Physical AI classification: map the workload to domain, sensor modality, failure mode, task metric, control boundary, and environment assumptions
- roadmap gate aggregation: combine domain, model, transformer/VLA, weight update, calibration/drift, sensor, control, compiler, runtime, power, accuracy, and evidence integrity into one decision view
- adapter registry: know which toolkit or service can prove which part of the stack
- adapter probing: tell the user whether AIHWKIT, CrossSim, analog-mlir, SST/Golem, ALPINE/gem5-X, board runtime, power/thermal, and task-metric services are configured or missing
- evidence normalization: convert toolkit outputs into known artifact types such as `analog_error_simulation`, `compiler_mapping`, `board_runtime`, `power_thermal`, and `task_accuracy`
- evidence validation: reject artifacts that lack provenance, scope, units, task metric, compatible package settings, or required fields
- claim discipline: keep measured, simulated, replayed, estimated, failed, and source-checked evidence separate
- roadmap gap generation: rank the next engineering work by claim impact, evidence importance, implementation risk, and customer relevance
- archive generation: export the full reasoning chain for diligence and technical review

### Toolkit-Backed Capabilities

The external toolkits become proof providers inside the platform:

- AIHWKIT answers whether analog noise, drift, converter limits, programming variation, and hardware-aware training assumptions damage the model.
- AIHWKIT-Lightning makes larger hardware-aware simulation sweeps practical for transformer-scale or LLM-adjacent models.
- CrossSim answers whether crossbar parasitics, bit slicing, ADC ranges, read noise, and programming errors preserve task accuracy.
- TxSim, XBTorch, and RxNN-style tools answer deeper training, write-update, and memristor-device behavior questions when those adapters are available.
- analog-mlir answers whether the graph can be partitioned, weight-isolated, lowered, and represented as an analog/digital execution task graph.
- SST/Golem answers whether compiler output still works inside a cycle-level CPU/co-processor simulation with realistic dispatch and synchronization overhead.
- ALPINE/gem5-X answers whether full-system CPU, memory hierarchy, runtime, and OS overhead erode the analog advantage.
- attention partitioners answer which transformer pieces are static analog candidates and which dynamic attention, Softmax, LayerNorm, and score-value regions require digital, mixed-signal, pruning, or rewrite paths.
- LIMCA-style design exploration can later propose candidate crossbar/macro architecture directions under power, area, and accuracy constraints.

### End-To-End Answer Contract

The platform should convert all of that into one package-level answer:

```text
Can it run?
  yes / partial / no / unknown

What proves it?
  measured evidence, imported toolkit evidence, simulation, compiler mapping, local estimate, source-checked context

What breaks?
  unsupported operators, analog accuracy loss, attention bottlenecks, missing compiler path,
  sensor/control boundary gaps, weight-update limits, calibration/drift risk, missing board/power evidence

What must be built or measured next?
  specific adapter, experiment, compiler pass, rewrite, board trace, power trace, calibration sweep,
  endurance test, task-accuracy run, or archive/evidence import

What can we safely claim?
  exact claim level plus what not to claim
```

## Investor And Customer Capability Narrative

This page should explain the product as an end-to-end evidence system. The investor or customer should understand that the platform is not another benchmark viewer. It is a structured decision engine for analog AI deployment.

The platform's strategic value is that it compresses a difficult diligence process into one repeatable workflow:

```text
representative workload
  -> analog fit analysis
  -> toolkit-backed simulation and compiler evidence
  -> full-system and board evidence import
  -> claim readiness
  -> roadmap gap plan
  -> exportable diligence package
```

### What The Investor Should See

An investor should be able to use the page to answer:

- whether the company has a repeatable way to qualify workloads, not just a one-off demo
- whether the chip roadmap is tied to evidence gates rather than vague market claims
- whether Physical AI, transformer, robotics, and sensor claims are separated from simpler fixed-weight edge inference
- whether the team knows which parts of the system are analog, digital, unsupported, simulated, measured, or still missing
- whether external tools are being used as disciplined evidence sources rather than name-dropping
- whether future engineering work is ranked by claim impact and customer relevance

Investor-facing output:

```text
This company can identify which customer workloads are credible now,
which claims are blocked,
which measurements would unlock stronger claims,
and which roadmap investments matter most.
```

### What The Customer Should See

A customer should be able to use the page to answer:

- whether their model can plausibly run on the chip
- which parts of their model are compatible with analog execution
- which operators remain digital or unsupported
- whether sensor, control, latency, power, calibration, and task-accuracy costs are included
- whether the current answer is based on measured hardware, simulation, compiler mapping, local estimates, or assumptions
- what evidence they should request before a pilot or design win

Customer-facing output:

```text
Here is what your workload does on this chip path today.
Here is what is proven.
Here is what is not proven.
Here is the exact next evidence needed before deployment.
```

### What The Internal Team Should See

The founder, product lead, ML engineer, compiler engineer, and hardware engineer should all see the same roadmap, but from different angles:

- founder: which roadmap gaps block fundraise, customer, and market claims
- product lead: which use cases are real product targets versus research distractions
- ML engineer: which model regions need rewriting, quantization, partitioning, or hardware-aware training
- compiler engineer: which operators and graph patterns need lowering, placement, tiling, or fallback support
- hardware engineer: which silicon, board, power, thermal, drift, endurance, and calibration measurements are missing
- customer success or field engineering: which statements are safe during customer technical review

## Capability Matrix

The platform should expose capabilities as product modules. Each module must answer a user question, produce backend artifacts, show a frontend panel, and state what it proves.

| Capability | User Question | Backend Artifacts | Toolkit Or Evidence Source | Frontend Output | What It Proves | What It Does Not Prove |
| --- | --- | --- | --- | --- | --- | --- |
| Workload credibility | Can this workload credibly run on this chip? | `physical_ai_roadmap`, `claim_readiness`, `evidence_brief` | all validated artifacts | status, proof, breaks, next work, safe claim | package-level decision quality | silicon performance by itself |
| Physical AI domain fit | Is this the right physical-world workload? | `physical_ai_map` | user profile, source-checked context, task settings | domain, modality, metric, failure mode | relevance of workload and system framing | hardware compatibility |
| Model/operator fit | Which parts map to analog? | deployment analysis, `rewrite_plan` | ONNX/local graph analysis, compiler evidence | analog/digital/fallback/unsupported regions | graph suitability | accuracy, power, or runtime alone |
| Analog error simulation | Does analog physics damage accuracy? | `analog_error_simulation` | AIHWKIT, CrossSim, TxSim, XBTorch, RxNN-style adapters | noise/drift/parasitic/converter sensitivity | modeled robustness under analog assumptions | measured board behavior |
| Compiler mapping | Can the graph reach an analog runtime? | `compiler_mapping`, `compiler_ecosystem_readiness` | analog-mlir, attention partitioner, compiler services | extracted layers, isolated weights, task graph, unsupported ops | compiler feasibility | physical accuracy or power |
| Transformer/VLA partition | Is this more than static projection mapping? | `vla_readiness`, `attention_partition_readiness` | attention partitioner, graph analysis | static projections, dynamic attention, Softmax, LayerNorm, rewrite paths | whether transformer regions have a credible hybrid plan | full VLA readiness without system evidence |
| Weight update readiness | Can the chip support the needed update pattern? | `weight_update_readiness` | update measurements, AIHWKIT/TxSim-style simulation, endurance evidence | fixed, periodic, adapter, or adaptive-blocked status | update-claim boundary | frequent adaptation without write evidence |
| Calibration and drift | Does the chip stay accurate in physical conditions? | `calibration_drift_readiness` | drift sweeps, calibration logs, board/lab evidence | temperature, voltage, aging, recalibration, fallback | reliability evidence direction | production qualification alone |
| Sensor boundary | Are front-end costs counted? | `sensor_boundary_readiness` | AFE specs, preprocessing traces, modality settings | sensor ownership, preprocessing, sync, latency, energy | end-to-end input cost visibility | neural model performance |
| Deterministic control boundary | Where does inference stop and control begin? | `control_boundary` | runtime profile, safety/control settings | handoff, jitter, safety monitor, fallback | control responsibility clarity | actuator safety certification |
| Runtime and power evidence | Does the system meet latency/energy constraints? | `measurement_evidence`, `board_runtime`, `power_thermal` | board service, SST/Golem, ALPINE/gem5-X, power traces | latency, jitter, energy, thermal, host overhead | measured or simulated runtime/power state | task accuracy unless paired with metric data |
| Task accuracy | Does the mapped workload still solve the task? | `task_accuracy`, `claim_readiness` | task metric service, imported benchmark/lab results | pre/post mapping accuracy and threshold | task-level correctness | power or compiler feasibility |
| Evidence integrity | Can reviewers audit the claim chain? | `evidence_audit`, `adapter_runs`, archive files | all sources | provenance, validation, failed runs, assumptions | diligence readiness | stronger technical claims by itself |

## Page-Level Product Specification

The HTML review page should read like a product capability deck and an implementation specification at the same time. It should explain the system from the top down, then let reviewers inspect the detailed machinery.

### Page Section 1: Executive Answer

Purpose:

Give a founder, investor, or customer the answer in the first screen.

Content:

- central question
- direct package answer: credible, partial, blocked, or unknown
- one-line safe claim
- one-line blocked claim
- top three proof sources
- top three breaks
- top three next actions

Backend dependencies:

- `physical_ai_roadmap`
- `claim_readiness`
- `evidence_brief`
- `evidence_audit`

Investor value:

Shows whether the company has a repeatable evidence process.

Customer value:

Shows whether the customer's workload deserves deeper technical work.

### Page Section 2: Workload And Chip Context

Purpose:

Make the scope of the answer clear.

Content:

- model name and source
- model type: CNN, MLP, RNN, transformer, multimodal, VLA-adjacent, classical ML, or custom graph
- domain: wearable, camera, industrial sensor, infrastructure, robot, vehicle, agriculture, defense/aerospace, ambient hardware, or other physical-world system
- modality: audio, image, video, event vision, tactile, IMU, radar, lidar, RF, biosignal, multimodal, or synthetic tensor
- deployment setting: lab, simulator, edge device, board prototype, customer pilot, or production target
- chip assumptions: analog memory type, array dimensions, converter precision, supported operators, host processor, runtime mode, calibration profile

Backend dependencies:

- model import
- deployment package settings
- `physical_ai_map`
- `sensor_boundary_readiness`
- `control_boundary`

What it prevents:

It prevents generic claims that do not specify the physical system, sensor path, task metric, or chip target.

### Page Section 3: Analog Fit And Model Mapping

Purpose:

Show what actually maps to analog compute.

Content:

- total operator count
- analog-friendly operator count
- digital-required operator count
- unsupported operator count
- fallback operator count
- analog/digital boundary crossings
- memory movement risk
- ADC/DAC conversion points
- layer table with placement, reason, evidence source, and rewrite recommendation

Backend dependencies:

- graph analyzer
- operator classifier
- compiler mapping imports
- `rewrite_suggestions`
- `rewrite_plan`

Toolkit support:

- analog-mlir for compiler placement
- attention partitioner for transformer-specific partitioning
- ONNX/local analysis as the baseline when compiler evidence is missing

What it proves:

It proves whether there is a plausible mapping strategy. It does not prove that the mapped model is accurate, fast, or energy efficient.

### Page Section 4: Toolkit Evidence Status

Purpose:

Make every external toolkit useful and bounded.

Content:

- toolkit name
- connection status: missing, configured, runnable, failed, imported, validated
- normalized artifact type
- what the toolkit can prove
- what the toolkit cannot prove
- required input files
- expected output schema
- latest run status
- failure reason and next fix

Backend dependencies:

- adapter registry
- adapter probe
- adapter execution plan
- connection playbook
- evidence templates
- adapter run audit

Investor value:

Shows that the company has an extensible evidence architecture and can plug in better tools over time.

Customer value:

Shows whether missing evidence is a tooling setup issue, a model issue, or a hardware issue.

### Page Section 5: Analog Physics And Accuracy Risk

Purpose:

Explain whether analog non-idealities break the workload.

Content:

- drift sensitivity
- programming noise sensitivity
- read noise sensitivity
- IR drop or parasitic resistance risk
- ADC/DAC precision risk
- bit slicing assumptions
- quantization impact
- post-mapping task accuracy
- simulation configuration and provenance

Backend dependencies:

- `analog_error_simulation`
- `calibration_drift_readiness`
- `task_accuracy`
- `measurement_evidence`

Toolkit support:

- AIHWKIT
- AIHWKIT-Lightning
- CrossSim
- TxSim
- XBTorch
- RxNN-style memristor simulators

What it proves:

It proves whether simulation suggests the workload can tolerate analog imperfections. It does not prove measured board accuracy unless imported board/task evidence exists.

### Page Section 6: Transformer And VLA Partition

Purpose:

Prevent transformer/VLA overclaiming.

Content:

- static projection candidates: WQ, WK, WV, WO, FFN
- dynamic attention blockers: QK^T, score-value, dynamic activation matrix multiplication
- Softmax and LayerNorm boundary
- KV cache and memory movement risk
- analog pruning candidate
- softmax-free or hardware-friendly rewrite candidate
- digital co-processor requirement
- claim boundary for VLA readiness

Backend dependencies:

- `vla_readiness`
- `attention_partition_readiness`
- `compiler_mapping`
- `weight_update_readiness`
- `rewrite_plan`

Toolkit support:

- attention partitioner
- analog-mlir
- AIHWKIT-Lightning for larger simulation sweeps
- SST/Golem or ALPINE/gem5-X for system-level runtime simulation

What it proves:

It proves whether the transformer has a credible hybrid analog/digital strategy. Mapping projection layers alone must not become a broad VLA-readiness claim.

### Page Section 7: Weight Update And Adaptation

Purpose:

Separate fixed-weight analog inference from adaptive Physical AI.

Content:

- update class: fixed-weight ready, periodic-update candidate, adapter-update candidate, or adaptive Physical AI blocked
- update scope: full model, selected layers, embedding table, action head, LoRA/adapter block, calibration constants, or unsupported
- update frequency: factory-only, rare service update, per-customer update, fleet update, per-device personalization, or frequent local adaptation
- write latency evidence
- write energy evidence
- endurance evidence
- write voltage evidence
- retention evidence
- post-update accuracy evidence
- rollback evidence
- recalibration cost

Backend dependencies:

- `weight_update_readiness`
- `measurement_evidence`
- `claim_readiness`
- `evidence_audit`

Toolkit support:

- AIHWKIT or TxSim-style tools for modeled update behavior
- hardware lab evidence for endurance, write energy, retention, and rollback

What it proves:

It proves the safe boundary of update claims. It should block adaptive Physical AI claims when update evidence is missing.

### Page Section 8: Sensor, Control, Runtime, And Power

Purpose:

Move from model-only evaluation to physical-system evaluation.

Content:

- sensor front-end ownership
- AFE, event, tactile, sync, preprocessing, and buffering costs
- sensor-to-output latency
- sensor-to-output energy
- deterministic control handoff
- jitter budget
- safety monitor and fallback behavior
- board runtime latency
- host overhead
- power and thermal trace status

Backend dependencies:

- `sensor_boundary_readiness`
- `control_boundary`
- `board_runtime`
- `power_thermal`
- `measurement_evidence`
- `physical_ai_roadmap`

Toolkit support:

- SST/Golem for cycle-level co-simulation
- ALPINE/gem5-X for full-system simulation
- board runtime and power/thermal services for measured evidence

What it proves:

It proves whether the analog benefit survives real physical system boundaries. It does not let a low analog-core number hide sensor, host, control, or converter costs.

### Page Section 9: Claim Readiness And Safe Language

Purpose:

Turn technical evidence into usable commercial and roadmap language.

Content:

- supported claims
- needs-review claims
- blocked claims
- production readiness status
- safe customer wording
- safe investor wording
- do-not-claim list
- evidence required to unlock each blocked claim

Backend dependencies:

- `claim_readiness`
- `evidence_brief`
- `evidence_audit`
- `physical_ai_roadmap`

What it proves:

It proves that the company can govern claims. This matters because analog AI companies can easily overstate efficiency, VLA readiness, or adaptive behavior when only narrow simulation exists.

### Page Section 10: Roadmap Gap Table And Work Orders

Purpose:

Turn blockers into engineering action.

Content:

- gap title
- blocked claim
- required artifact
- owner role
- priority
- estimated implementation risk
- customer or investor impact
- acceptance evidence
- recommended next experiment

Backend dependencies:

- `physical_ai_roadmap`
- `rewrite_work_order`
- `adapter_execution_plan`
- `connection_playbook`

What it enables:

The team can leave a review with concrete next work instead of a vague "needs more validation" conclusion.

### Page Section 11: Archive And Diligence Package

Purpose:

Make the answer auditable.

Content:

- package manifest
- source model reference
- package settings
- all generated JSON artifacts
- all imported evidence
- adapter run history
- failed connector attempts
- source-check register
- evidence brief
- decision report
- roadmap gap table
- safe claims and blocked claims

Backend dependencies:

- deployment archive builder
- artifact persistence
- evidence audit
- source-check register

Investor value:

The archive makes technical diligence reproducible.

Customer value:

The archive gives a technical team enough evidence to review scope, assumptions, and next steps.

## First Principles

### 1. AIMC Is A Physical Execution Substrate, Not Just A Faster Matrix Library

Analog in-memory compute works because neural network weights can be represented as physical conductance states in memory devices. Inputs are applied as voltages or currents, multiplication happens through device conductance, and accumulation happens naturally on wires or bitlines.

This is powerful because dense matrix-vector multiplication can happen near or inside memory, reducing data movement.

But it also means the computation is no longer ideal digital math. It is physical math.

The platform must therefore ask:

- are the weights stable enough to live in analog memory?
- are the operators mostly dense linear algebra?
- how much energy is spent in ADCs, DACs, memory movement, host control, and fallback paths?
- how much accuracy is lost to drift, noise, IR drop, programming variation, quantization, and parasitics?
- does the full physical system still meet the task metric?

### 2. Analog MAC Efficiency Is Not A Product Claim By Itself

A strong analog core is not enough. The real claim depends on completed inference:

```text
sensor/input -> preprocessing -> model execution -> digital support -> control or output
```

The platform must count:

- analog array compute
- digital operators
- ADC/DAC conversion
- memory movement
- host orchestration
- fallback operators
- calibration overhead
- update/programming cost
- thermal behavior
- task accuracy after mapping

### 3. Simulation Is Useful, But It Must Stay Labeled As Simulation

AIHWKIT, CrossSim, analog-mlir, SST/Golem, ALPINE/gem5-X, and related tools can produce strong evidence for different layers of the stack.

They do not all prove the same thing.

The platform must keep these categories separate:

- differentiable hardware-aware simulation
- crossbar accuracy simulation
- compiler placement
- cycle-level co-simulation
- full-system simulation
- local replay fixture
- measured board evidence
- measured power/thermal evidence
- task accuracy evidence
- source-checked research context

No simulation artifact should silently become a measured hardware claim.

### 4. Transformer And VLA Workloads Break The Simple Analog Story

CNNs, MLPs, projections, and many linear layers fit the classic weight-stationary analog story better than dynamic attention.

Transformer attention creates two major issues:

- dynamic activation-to-activation matrix multiplication, especially QK^T and score-value operations
- non-linear normalization such as Softmax and sometimes LayerNorm

The platform must separate:

- static projection weights that may map to analog memory
- FFN weights that may map to analog memory
- dynamic QK and attention-score work that may need digital or specialized mixed-signal paths
- Softmax/LayerNorm that may remain digital or require model rewrite
- analog pruning or softmax-free attention alternatives
- weight update or adapter paths for personalization and VLA adaptation

## Toolkit Families And What They Allow Us To Do

### AIHWKIT

Role:

```text
differentiable hardware-aware simulation
```

What it is:

AIHWKIT is IBM's open-source Python toolkit for exploring analog in-memory computing with AI workloads. It is built around PyTorch integration and supports hardware-aware training and inference simulation.

What it allows:

- simulate analog non-idealities inside PyTorch workflows
- evaluate how device noise, drift, programming noise, update behavior, and converter precision affect model behavior
- run hardware-aware training or fine-tuning experiments
- test whether a model is robust to analog execution assumptions before using board time
- model analog weight update behavior as a first-class concern

How our platform uses it:

Adapter target:

```text
sim.aihwkit
```

Normalized evidence:

```text
analog_error_simulation
```

Platform output:

- analog error profile
- drift sensitivity
- converter sensitivity
- IR-drop or spatial-error assumptions, when available
- post-mapping accuracy impact estimate
- update/write non-ideality risk, when modeled

Claim boundary:

AIHWKIT output can support "hardware-aware simulation suggests this model may tolerate these analog assumptions." It cannot prove board latency, board power, production reliability, or compiler placement by itself.

### AIHWKIT-Lightning

Role:

```text
large-scale accelerated hardware-aware simulation
```

What it allows:

- faster simulation of larger models
- more practical exploration for transformer-scale or LLM-adjacent experiments
- GPU-accelerated hardware-aware sweeps

How our platform should treat it:

AIHWKIT-Lightning is not a separate claim category. It is an implementation backend for the AIHWKIT-style adapter when scale matters.

Adapter path:

```text
sim.aihwkit
```

Additional output fields:

- simulation backend: baseline AIHWKIT or Lightning
- model scale
- array tiling assumptions
- runtime/memory cost of simulation

### CrossSim

Role:

```text
crossbar accuracy simulation and device-to-algorithm co-design
```

What it is:

CrossSim is Sandia's GPU-accelerated Python simulator for analog in-memory computing. It focuses on how resistive crossbar hardware effects affect algorithmic solution quality.

What it allows:

- simulate matrix workloads on analog crossbar assumptions
- evaluate bit slicing and multiple devices per logical weight
- test programming errors, read noise, ADC range choices, and parasitic wire resistance
- connect crossbar-level physical assumptions to model-level accuracy
- explore architecture and device settings before board evidence exists

How our platform uses it:

Adapter target:

```text
sim.crosssim
```

Normalized evidence:

```text
analog_error_simulation
```

Platform output:

- crossbar array assumptions
- bit-slicing plan
- ADC range policy
- parasitic resistance assumptions
- programming/read noise assumptions
- task accuracy impact, if paired with task metric

Claim boundary:

CrossSim can support crossbar-level accuracy and non-ideality discussion. It does not prove full-system runtime, power, control safety, sensor cost, or production readiness by itself.

### TxSim

Role:

```text
training-phase crossbar non-ideality simulation
```

What it allows:

- evaluate crossbar non-idealities during forward propagation, backward propagation, and update
- model DAC non-linearity, write variation, stochastic update noise, and device variability
- assess whether training or adaptation is plausible under analog update assumptions

How our platform should use it:

TxSim is a future adapter family for the weight-update and hardware-aware-training path.

Potential adapter:

```text
sim.training-update-crossbar
```

Normalized evidence:

```text
analog_error_simulation
weight_update_readiness
```

Claim boundary:

TxSim-style output can inform whether analog-aware training or repeated update behavior is plausible. It does not replace endurance, write-energy, write-latency, retention, rollback, or post-update board accuracy evidence.

### XBTorch

Role:

```text
PyTorch-native crossbar modeling and co-design
```

What it allows:

- model crossbar-based deep learning accelerators inside PyTorch
- explore device-level modeling, cross-layer co-design, inference-time fault tolerance, and emerging memory assumptions
- compare hardware-aware training and inference paths under different device models

How our platform should use it:

XBTorch belongs in the same adapter family as AIHWKIT and TxSim, but with a stronger focus on crossbar co-design.

Potential adapter:

```text
sim.xbtorch
```

Normalized evidence:

```text
analog_error_simulation
```

Claim boundary:

It can support algorithm/hardware co-design evidence. It should not become measured hardware or compiler evidence unless the normalized artifact includes those fields from a real toolchain.

### Synaptogen / RxNN-Style Memristor Simulation

Role:

```text
memristor device behavior simulation for larger neural networks
```

What it allows:

- simulate memristor array behavior in PyTorch-like model execution
- include richer device behavior than idealized matrix multiplication
- test how stochastic or non-linear memristor properties affect model behavior

How our platform should use it:

This is a future adapter family for device-specific analog error simulation.

Potential adapter:

```text
sim.memristor-device
```

Normalized evidence:

```text
analog_error_simulation
```

Claim boundary:

It supports device behavior analysis, not board performance or production yield.

### analog-mlir

Role:

```text
compiler lowering from tensor/linalg graph to analog execution IR
```

What it allows:

- outline supported analog-friendly layers
- convert digital tensor/linalg kernels into analog execution operations
- isolate static weights from activation flow
- build analog/digital task graphs
- lower the task graph toward a simulator runtime such as Golem
- expose unsupported operators and placement boundaries

How our platform uses it:

Adapter target:

```text
compiler.analog-mlir-golem
```

Normalized evidence:

```text
compiler_mapping
```

Platform output:

- operator placements
- analog layer extraction
- static weight isolation report
- tiling and array mapping
- digital fallback regions
- runtime graph metadata
- unsupported operators

Claim boundary:

analog-mlir output supports compiler mapping and graph-lowering claims. It does not prove analog accuracy, runtime latency, power, or task accuracy without additional evidence.

### SST / Golem

Role:

```text
cycle-level hardware/software co-simulation
```

What it allows:

- simulate analog accelerator execution as part of a CPU/system environment
- model dispatch from a CPU into an analog array runtime
- measure cycle-level overheads, synchronization cost, memory bottlenecks, and task scheduling
- combine ideal or CrossSim-backed analog execution with system-level timing

How our platform uses it:

Adapter target:

```text
system.sst-golem
```

Normalized evidence:

```text
board_runtime
```

Evidence label:

```text
cycle-level co-simulation
```

Claim boundary:

SST/Golem evidence can support simulated runtime and hardware/software scheduling discussion. It is not measured board evidence.

### ALPINE / gem5-X

Role:

```text
full-system AIMC simulation
```

What it allows:

- simulate CPU integration, memory hierarchy, custom ISA/runtime dispatch, and operating-system/runtime overhead
- test how much full-system behavior erodes core analog gains
- evaluate software library integration and system bottlenecks

How our platform uses it:

Adapter target:

```text
system.alpine-gem5x
```

Normalized evidence:

```text
board_runtime
```

Evidence label:

```text
full-system simulation
```

Claim boundary:

ALPINE/gem5-X output can support full-system simulation claims. It cannot be sold as measured silicon evidence.

### LIMCA

Role:

```text
automated IMC crossbar architecture design exploration
```

What it allows:

- explore architecture design choices under power, area, and accuracy constraints
- generate or validate circuit/netlist-level candidates
- shorten early design-space exploration

How our platform should use it:

LIMCA is a future roadmap adapter, not part of the first package evidence loop.

Potential adapter:

```text
dse.limca
```

Normalized evidence:

```text
architecture_design_candidate
```

Potential platform output:

- candidate array configuration
- power/area/accuracy constraints
- SPICE validation status
- design-space tradeoff table
- recommended next silicon or macro experiment

Claim boundary:

LIMCA-style output is design-space exploration. It cannot prove model compatibility, board runtime, or production performance.

## External Toolkit Contribution Contract

This section explains, in plain language, what each external toolkit gives the end user through our platform.

The user should not need to install every tool, read every paper, or understand every simulator. Our platform should translate each toolkit into a clear product answer:

```text
What did this tool check?
What did it find?
How much should we trust it?
What claim can it support?
What claim is still blocked?
What should we do next?
```

### How The Platform Uses External Toolkits

The platform should treat each external toolkit as a specialist reviewer.

- Some tools review analog accuracy risk.
- Some tools review compiler mapping.
- Some tools review transformer partitioning.
- Some tools review runtime and system overhead.
- Some tools review architecture design choices.
- Some tools are future options that we track but do not rely on yet.

The platform's job is to make all of these outputs comparable. It does this by converting them into a small number of normalized evidence types:

- `analog_error_simulation`: evidence about analog noise, drift, parasitics, converter limits, programming error, and task accuracy under analog assumptions
- `compiler_mapping`: evidence about which model operators can be placed on analog compute and which must remain digital
- `attention_partition_readiness`: evidence about whether transformer/VLA attention has a credible analog/digital split
- `weight_update_readiness`: evidence about whether weights or adapters can be updated after deployment
- `board_runtime`: evidence about latency, jitter, host overhead, and runtime behavior
- `power_thermal`: evidence about energy, power, temperature, and thermal limits
- `task_accuracy`: evidence about whether the model still meets the user-facing task metric
- `architecture_design_candidate`: evidence about future chip or macro design choices

### Toolkit 1: AIHWKIT

Plain-English purpose:

AIHWKIT helps answer: "If this neural network runs on imperfect analog memory instead of clean digital math, does the model still work?"

What the user gives our platform:

- model or model layers
- target precision assumptions
- analog memory assumptions
- drift/noise/programming assumptions
- task metric, if available
- calibration or update assumptions, if available

What our platform sends to the toolkit:

- selected analog-candidate layers
- weight and activation precision settings
- noise, drift, converter, and programming settings
- evaluation dataset or task metric hook, when available

What the toolkit gives back:

- simulated accuracy under analog assumptions
- sensitivity to drift
- sensitivity to programming noise
- sensitivity to ADC/DAC precision
- hardware-aware training or fine-tuning result, when used
- modeled write/update effects, when configured

What the end user sees:

```text
Analog simulation: completed
Accuracy impact: moderate
Main risk: drift and converter precision
Safe claim: simulation suggests this model may tolerate analog execution
Blocked claim: measured board accuracy is not proven
Next work: import board accuracy trace or run CrossSim parasitic sweep
```

What it can support:

- simulated analog robustness
- hardware-aware training discussion
- drift/noise sensitivity discussion
- early decision on whether a model is worth board testing

What it cannot support by itself:

- real chip latency
- real chip power
- production reliability
- compiler placement
- customer deployment readiness

Backend adapter:

```text
sim.aihwkit
```

Normalized artifact:

```text
analog_error_simulation
```

### Toolkit 2: AIHWKIT-Lightning

Plain-English purpose:

AIHWKIT-Lightning helps answer the same kind of question as AIHWKIT, but for larger models where normal simulation may be too slow.

What the user gets:

- faster sweeps for larger networks
- more practical testing for transformer-scale or LLM-adjacent experiments
- less waiting before deciding whether a workload deserves deeper validation

What the end user sees:

```text
Simulation backend: AIHWKIT-Lightning
Model scale: large
Sweep status: completed
Safe claim: larger analog-error simulation was run
Blocked claim: this is still simulation, not measured silicon
```

What it can support:

- larger hardware-aware simulation campaigns
- more realistic exploration of transformer-sized workloads

What it cannot support by itself:

- measured runtime
- measured energy
- full-system behavior
- production readiness

Backend adapter:

```text
sim.aihwkit
```

Normalized artifact:

```text
analog_error_simulation
```

### Toolkit 3: CrossSim

Plain-English purpose:

CrossSim helps answer: "Do crossbar hardware details damage the answer enough that the model stops being useful?"

What the user gives our platform:

- model or matrix workload
- target array size
- bit slicing assumptions
- ADC range assumptions
- device noise settings
- parasitic resistance assumptions
- task metric, if available

What our platform sends to the toolkit:

- candidate analog matrix operations
- crossbar array configuration
- device and circuit assumptions
- evaluation inputs or task accuracy hook

What the toolkit gives back:

- accuracy under crossbar assumptions
- effect of parasitic wire resistance
- effect of read noise
- effect of programming error
- effect of ADC range selection
- bit-slicing sensitivity

What the end user sees:

```text
Crossbar simulation: completed
Biggest break: parasitic resistance at selected array size
Accuracy after mapping: below target
Safe claim: current crossbar assumptions are risky
Next work: reduce array size, change bit slicing, recalibrate ADC range, or measure silicon
```

What it can support:

- crossbar-level accuracy risk
- device-to-model sensitivity
- design-space decisions before hardware is available

What it cannot support by itself:

- full-system runtime
- power trace
- control safety
- sensor front-end cost
- production readiness

Backend adapter:

```text
sim.crosssim
```

Normalized artifact:

```text
analog_error_simulation
```

### Toolkit 4: TxSim

Plain-English purpose:

TxSim helps answer: "If the analog device is involved during training or updates, do write errors and device variation make learning unstable?"

What the user gives our platform:

- training or fine-tuning setup
- model layers
- update assumptions
- write-variation assumptions
- device-variation assumptions

What the toolkit gives back:

- training-phase simulation
- forward-pass error impact
- backward-pass error impact
- update-step error impact
- stochastic write noise impact
- DAC nonlinearity impact

What the end user sees:

```text
Update simulation: available
Main risk: write variation during repeated updates
Safe claim: update behavior has been modeled
Blocked claim: endurance and write energy are not measured
Next work: import write-latency, write-energy, endurance, and post-update accuracy evidence
```

What it can support:

- early update-risk analysis
- analog-aware training discussion
- whether repeated updates are likely fragile

What it cannot support by itself:

- write endurance on real memory
- write energy on real silicon
- retention after update
- safe rollback
- adaptive Physical AI readiness

Potential backend adapter:

```text
sim.training-update-crossbar
```

Normalized artifacts:

```text
analog_error_simulation
weight_update_readiness
```

### Toolkit 5: XBTorch

Plain-English purpose:

XBTorch helps answer: "Can we study crossbar behavior while staying inside a PyTorch-style model workflow?"

What the user gives our platform:

- PyTorch model or converted model region
- crossbar device assumptions
- training or inference settings
- accuracy target

What the toolkit gives back:

- modeled crossbar behavior
- hardware-aware training result
- inference sensitivity result
- device-level modeling output
- fault or variation sensitivity, when configured

What the end user sees:

```text
PyTorch crossbar simulation: completed
Model sensitivity: acceptable under selected assumptions
Safe claim: PyTorch-native crossbar co-design simulation is available
Blocked claim: no board or compiler evidence yet
```

What it can support:

- model/hardware co-design exploration
- comparison of training and inference assumptions
- early fault or variation analysis

What it cannot support by itself:

- production chip performance
- compiler placement
- customer pilot readiness

Potential backend adapter:

```text
sim.xbtorch
```

Normalized artifact:

```text
analog_error_simulation
```

### Toolkit 6: RxNN And Synaptogen-Style Memristor Simulation

Plain-English purpose:

RxNN and Synaptogen-style tools help answer: "What happens if the analog memory device behaves like a real memristor instead of an ideal math block?"

What the user gives our platform:

- model or model region
- memristor device assumptions
- conductance or switching assumptions
- inference or training setting

What the toolkit gives back:

- simulated memristor behavior
- device nonlinearity impact
- device variability impact
- model accuracy under richer device assumptions

What the end user sees:

```text
Memristor simulation: available
Main risk: device nonlinearity
Safe claim: device-level simulation suggests a risk area
Blocked claim: measured device array behavior is not proven
```

What it can support:

- device-specific risk analysis
- memristor behavior discussion
- early silicon planning

What it cannot support by itself:

- real array yield
- board runtime
- power
- deployment readiness

Potential backend adapter:

```text
sim.memristor-device
```

Normalized artifact:

```text
analog_error_simulation
```

### Toolkit 7: analog-mlir

Plain-English purpose:

analog-mlir helps answer: "Can the model graph be translated into something an analog runtime could actually execute?"

What the user gives our platform:

- model graph
- supported operator list
- target analog array assumptions
- runtime target assumptions

What our platform sends to the toolkit:

- model graph or lowered representation
- candidate analog layers
- placement constraints
- target runtime information

What the toolkit gives back:

- extracted analog-friendly layers
- isolated static weights
- analog/digital task graph
- lowered runtime representation
- unsupported operators
- fallback regions
- placement metadata

What the end user sees:

```text
Compiler mapping: partial
Analog regions: Conv and Linear layers
Digital regions: Softmax, LayerNorm, dynamic attention
Unsupported regions: custom operator
Safe claim: compiler mapping exists for selected static layers
Blocked claim: full model does not compile to analog execution
Next work: rewrite unsupported operator or add compiler pass
```

What it can support:

- compiler feasibility
- operator placement
- analog/digital partitioning
- weight isolation claims

What it cannot support by itself:

- analog accuracy
- runtime latency
- power
- board behavior
- customer deployment readiness

Backend adapter:

```text
compiler.analog-mlir-golem
```

Normalized artifact:

```text
compiler_mapping
```

### Toolkit 8: SST/Golem

Plain-English purpose:

SST/Golem helps answer: "If the analog accelerator is connected to a processor in simulation, do dispatch, synchronization, and memory movement break the runtime story?"

What the user gives our platform:

- compiler output or runtime graph
- CPU/co-processor assumptions
- memory and bus assumptions
- analog array timing assumptions
- workload input profile

What the toolkit gives back:

- simulated cycle-level runtime
- CPU dispatch overhead
- synchronization overhead
- memory bottlenecks
- accelerator utilization
- runtime scheduling behavior

What the end user sees:

```text
System simulation: completed
Main break: host synchronization overhead
Analog core utilization: low
Safe claim: cycle-level simulation identifies runtime bottlenecks
Blocked claim: measured board latency is not proven
Next work: change dispatch path, reduce transfers, or measure board runtime
```

What it can support:

- simulated runtime feasibility
- system bottleneck discovery
- pre-silicon hardware/software co-design

What it cannot support by itself:

- measured board performance
- real power
- real thermal behavior
- production reliability

Backend adapter:

```text
system.sst-golem
```

Normalized artifact:

```text
board_runtime
```

Evidence label:

```text
cycle-level simulation
```

### Toolkit 9: ALPINE / gem5-X

Plain-English purpose:

ALPINE/gem5-X helps answer: "Does the analog accelerator still look useful when simulated inside a fuller computer system with CPU, memory, runtime, and operating-system behavior?"

What the user gives our platform:

- target system configuration
- model/runtime workload
- CPU and memory assumptions
- accelerator dispatch assumptions
- software library assumptions

What the toolkit gives back:

- full-system simulated runtime
- CPU overhead
- memory hierarchy effects
- software runtime overhead
- accelerator interaction with the rest of the system

What the end user sees:

```text
Full-system simulation: available
Main risk: memory hierarchy overhead reduces analog advantage
Safe claim: full-system simulation has been run
Blocked claim: measured silicon or board evidence is still missing
```

What it can support:

- full-system pre-silicon runtime analysis
- software/hardware integration discussion
- better estimate of how much analog core efficiency survives system overhead

What it cannot support by itself:

- measured hardware performance
- final energy efficiency
- customer production readiness

Backend adapter:

```text
system.alpine-gem5x
```

Normalized artifact:

```text
board_runtime
```

Evidence label:

```text
full-system simulation
```

### Toolkit 10: Attention Partitioner

Plain-English purpose:

The attention partitioner helps answer: "For a transformer or VLA-style model, which parts are realistic analog candidates and which parts must stay digital or be redesigned?"

What the user gives our platform:

- transformer or VLA-adjacent model
- sequence length and token shape assumptions
- precision assumptions
- target analog and digital resources
- latency and energy goals

What the toolkit gives back:

- static projection mapping candidates
- FFN mapping candidates
- dynamic QK boundary
- score-value boundary
- Softmax boundary
- LayerNorm boundary
- KV-cache and memory movement risk
- digital co-processor requirement
- analog pruning candidates
- softmax-free rewrite candidates

What the end user sees:

```text
Transformer partition: partial
Analog candidates: projection and FFN weights
Digital-required regions: QK^T, Softmax, score-value, LayerNorm
Safe claim: static transformer layers may be analog candidates
Blocked claim: full transformer or VLA readiness is not proven
Next work: add digital attention path, run system simulation, or rewrite attention block
```

What it can support:

- honest transformer partitioning
- VLA-readiness boundary
- rewrite planning
- co-processor planning

What it cannot support by itself:

- full model accuracy
- runtime speedup
- power reduction
- adaptive robotics readiness

Backend adapter:

```text
compiler.attention-partitioner
```

Normalized artifacts:

```text
compiler_mapping
attention_partition_readiness
```

### Toolkit 11: LIMCA-Style Design Exploration

Plain-English purpose:

LIMCA-style design exploration helps answer: "If the current chip design is not enough, what kind of crossbar or macro design should we explore next?"

What the user gives our platform:

- power target
- area target
- accuracy target
- memory technology assumptions
- candidate workload class
- design constraints

What the toolkit gives back:

- candidate crossbar or macro design
- power/area/accuracy tradeoff
- SPICE or circuit validation status, when available
- design-space ranking
- recommended next hardware experiment

What the end user sees:

```text
Design exploration: roadmap candidate
Suggested direction: smaller array with lower parasitic risk
Safe claim: candidate design direction identified
Blocked claim: product performance is not proven
Next work: run circuit validation and connect result to model-level simulation
```

What it can support:

- future architecture planning
- early macro design tradeoff discussion
- power/area/accuracy exploration

What it cannot support by itself:

- model compatibility
- board runtime
- production performance
- customer deployment readiness

Potential backend adapter:

```text
dse.limca
```

Normalized artifact:

```text
architecture_design_candidate
```

### Services That Are Not Research Toolkits But Are Required For Strong Claims

Some evidence must come from measurement services or internal lab systems, not from research simulators.

#### Board Runtime Service

Plain-English purpose:

Answers: "What happened on the actual board or prototype?"

Provides:

- measured latency
- jitter
- host overhead
- accelerator execution time
- fallback execution time
- runtime failures

Supports:

- prototype runtime claims
- board-level bottleneck analysis

Does not support:

- task accuracy unless paired with task metric evidence
- power unless paired with power evidence
- production readiness by itself

Normalized artifact:

```text
board_runtime
```

#### Power And Thermal Service

Plain-English purpose:

Answers: "How much energy and heat does the workload actually cost?"

Provides:

- energy per inference
- average power
- peak power
- temperature behavior
- thermal throttling evidence
- update/programming energy, when measured

Supports:

- measured energy and thermal claims
- separation of inference energy from update energy

Does not support:

- accuracy
- compiler mapping
- production reliability by itself

Normalized artifact:

```text
power_thermal
```

#### Task Metric Service

Plain-English purpose:

Answers: "Does the mapped model still solve the user's real task?"

Provides:

- baseline digital accuracy
- analog-mapped accuracy
- post-drift accuracy
- post-update accuracy
- task-specific metric
- pass/fail threshold

Supports:

- task-level correctness claims
- customer workload readiness discussion

Does not support:

- runtime
- power
- compiler feasibility by itself

Normalized artifact:

```text
task_accuracy
```

### What The User Should Understand From The Toolkit Section

The platform should make three ideas obvious:

1. Each toolkit answers a different part of the deployment question.
2. No single toolkit proves the whole chip story.
3. Our product creates value by combining toolkit outputs, measured evidence, and claim rules into one trustworthy answer.

The final user-facing summary should read like this:

```text
AIHWKIT says the model may tolerate analog noise.
CrossSim says the selected array size has parasitic risk.
analog-mlir says only some layers compile to analog execution.
The attention partitioner says dynamic attention must stay digital.
SST/Golem says host synchronization may erase some speedup.
Board power evidence is missing.
Task accuracy after analog mapping is missing.

Therefore:
This is a partial analog fit.
It is not yet a production-ready Physical AI claim.
The next work is compiler placement, crossbar simulation, board runtime, power trace, and task accuracy import.
```

### Attention Partitioners And Transformer-Specific Hardware Paths

Role:

```text
transformer/VLA partition planning
```

What they allow:

- distinguish static weight-stationary matrix operations from dynamic activation-to-activation attention work
- map WQ, WK, WV, WO, and FFN projections where appropriate
- route QK^T, Softmax, score-value, LayerNorm, and high-precision attention work to digital or specialized mixed-signal units
- identify analog pruning candidates
- identify softmax-free or hardware-friendly attention rewrite options

How our platform uses it:

Adapter target:

```text
compiler.attention-partitioner
```

Normalized evidence:

```text
compiler_mapping
```

Platform output:

- static projection mapping
- digital attention boundary
- Softmax and LayerNorm boundary
- dynamic activation-matmul boundary
- analog pruning candidates
- rewrite candidates
- blocked transformer claims

Claim boundary:

Projection mapping is not VLA readiness. The platform must block broad transformer/VLA claims until dynamic attention, non-linear layers, memory movement, converter cost, and task accuracy are accounted for.

## Platform Architecture

### Backend Responsibilities

The backend is the evidence engine.

It must:

- import a model
- analyze operators, shapes, and graph structure
- classify analog-friendly, digital-required, fallback, and unsupported operators
- estimate local runtime and energy as low-confidence baseline context
- register external toolkit adapters
- probe whether each toolkit is installed or configured
- run local adapters when available
- accept normalized external evidence
- validate evidence before import
- rebuild package claims after evidence import
- preserve failed adapter runs as audit records
- export a reproducible archive

### Backend Artifact Model

Core artifacts:

- `deployment_package_readiness`
- `physical_ai_roadmap`
- `physical_ai_map`
- `vla_readiness`
- `weight_update_readiness`
- `calibration_drift_readiness`
- `control_boundary`
- `sensor_boundary_readiness`
- `compiler_ecosystem_readiness`
- `toolchain_readiness`
- `connection_playbook`
- `adapter_execution_plan`
- `adapter_connection_kit`
- `adapter_evidence_templates`
- `adapter_connection_self_test`
- `adapter_integration_readiness`
- `external_connector_contract`
- `measurement_evidence`
- `claim_readiness`
- `evidence_audit`
- `evidence_brief`
- `decision_report`
- `rewrite_suggestions`
- `rewrite_plan`
- `rewrite_work_order`

Toolkit-derived normalized evidence:

- AIHWKIT -> `analog_error_simulation`
- CrossSim -> `analog_error_simulation`
- TxSim/XBTorch/Synaptogen-style tools -> `analog_error_simulation`, and possibly `weight_update_readiness`
- analog-mlir -> `compiler_mapping`
- attention partitioner -> `compiler_mapping`
- SST/Golem -> `board_runtime` with simulation provenance
- ALPINE/gem5-X -> `board_runtime` with full-system simulation provenance
- board service -> `board_runtime` with measured/prototype provenance
- power/thermal service -> `power_thermal`
- task metric service -> `task_accuracy`

### Backend APIs

Existing and target API families:

```text
POST /models/import
POST /models/{model_id}/deployment-package
GET  /deployment-packages/{package_id}/artifacts
GET  /deployment-packages/{package_id}/physical-ai-roadmap
GET  /deployment-packages/{package_id}/compiler-ecosystem-readiness
GET  /deployment-packages/{package_id}/connection-playbook
GET  /adapters
GET  /adapters/{adapter_id}/probe
POST /adapters/{adapter_id}/run
POST /evidence/validate
POST /evidence/import
POST /evidence/import-batch
GET  /deployment-packages/{package_id}/claim-readiness
GET  /deployment-packages/{package_id}/evidence-audit
GET  /deployment-packages/{package_id}/archive
```

### Adapter Contract

Every adapter must define:

- adapter id
- name
- category
- status
- configuration requirements
- probe checks
- normalized output type
- minimum required fields
- evidence claim boundary
- do-not-claim rule
- next action

Every adapter run must store:

- adapter id
- status
- raw request reference
- raw response reference
- normalized output, if present
- provenance
- confidence
- failure details
- whether the output is claim evidence or audit trail only

### Evidence Rules

Evidence can move claims only when:

- it matches a known source id
- it passes schema validation
- it includes provenance
- it matches the package settings or clearly states its scope
- it has a compatible measurement or simulation status
- the relevant claim requires that source

Evidence cannot move claims when:

- it is only a source-checked paper example
- it is only a failed adapter attempt
- it is local simulation but the claim requires measured board evidence
- it is compiler mapping but the claim is about power or accuracy
- it is analog error simulation but the claim is about full-system latency
- it is a replay fixture but the claim requires external or measured evidence

## Frontend Specification

The frontend is the operating surface for the roadmap.

It should not feel like a marketing page. It should feel like a technical workbench.

### Main Views

#### 1. Package Overview

Shows:

- model name
- target profile
- modality
- calibration profile
- runtime mode
- readiness stage
- safe claim
- archive link
- current evidence status

Purpose:

Give the user a fast answer:

```text
Is this package blocked, analysis-only, simulator-review-ready, prototype-review-ready, or stronger?
```

#### 2. Workload Credibility Answer

Shows:

- answer status: credible, partial, blocked, or unknown
- workload summary: domain, modality, model type, deployment context, and chip target
- proof exists: measured, imported, simulated, compiler-derived, locally estimated, and source-checked evidence
- breaks: operators, attention regions, analog/digital boundaries, calibration/drift gaps, update gaps, sensor/control gaps, and missing tool paths
- next work: ranked measurements, adapters, simulations, compiler passes, rewrites, or hardware experiments
- safe claim: what can be said now
- blocked claim: what must not be said yet

Purpose:

Answer the product question directly:

```text
Can this workload credibly run on this analog chip, what proof exists, what breaks, and what must be built or measured next?
```

This view should be the user's first stop after package creation. The rest of the workbench explains the answer.

#### 3. Physical AI Roadmap

Shows all gates:

- domain fit
- model fit
- transformer/VLA fit
- weight update fit
- calibration/drift fit
- control boundary fit
- sensor boundary fit
- compiler fit
- simulation-to-silicon fit
- attention partition fit
- runtime/power fit
- task accuracy fit
- evidence integrity

Each gate shows:

- status
- risk
- evidence state
- safe claim
- next action

Purpose:

Make the whole roadmap visible in one place.

#### 4. Toolkit Connections

Shows:

- AIHWKIT
- CrossSim
- analog-mlir/Golem
- SST/Golem
- ALPINE/gem5-X
- attention partitioner
- ONNX Runtime
- board runtime
- power/thermal
- task accuracy

Each toolkit row shows:

- installed/configured/missing
- what it proves
- what it does not prove
- required environment or service
- normalized artifact expected
- run/probe status

Purpose:

Turn "we need a simulator" into a concrete connection plan.

#### 5. Model Mapping

Shows:

- layers/operators
- analog placement
- digital placement
- fallback placement
- unsupported operators
- boundary crossings
- memory movement
- ADC/DAC conversion points

Purpose:

Show what actually fits the chip.

#### 6. Transformer/VLA Partition

Shows:

- static projection mapping
- FFN mapping
- dynamic QK boundary
- score-value boundary
- Softmax boundary
- LayerNorm boundary
- memory and conversion bottlenecks
- analog pruning candidates
- rewrite candidates

Purpose:

Prevent false transformer/VLA claims.

#### 7. Weight Update Readiness

Shows:

- fixed-weight readiness
- occasional update candidate
- adapter update candidate
- adaptive Physical AI blocked
- write latency evidence
- write energy evidence
- endurance evidence
- retention evidence
- post-update accuracy evidence
- rollback evidence

Purpose:

Make adaptive claims impossible without update proof.

#### 8. Calibration And Drift

Shows:

- calibration profile
- temperature range
- voltage range
- drift evidence
- aging evidence
- weak-row/weak-cell handling
- recalibration requirement
- failure behavior

Purpose:

Keep Physical AI reliability honest.

#### 9. Sensor Boundary

Shows:

- expected sensors
- AFE ownership
- event/tactile/sync handling
- preprocessing cost
- sensor-to-output latency
- sensor-to-output energy

Purpose:

Prevent inference-only energy claims from hiding front-end cost.

#### 10. Control Boundary

Shows:

- inference role
- deterministic controller role
- actuator handoff
- jitter budget
- safety monitor
- fallback behavior

Purpose:

Separate neural inference from real-time control and safety.

#### 11. Evidence Import

Shows:

- source selector
- JSON template
- validation result
- preview of affected claims
- before/after claim status
- import action

Purpose:

Let users attach real evidence without corrupting claim logic.

#### 12. Claim Readiness

Shows:

- supported lab claims
- needs-review claims
- blocked claims
- production claim status
- what to say
- what not to say

Purpose:

Create safe customer/investor language.

#### 13. Archive And Diligence Package

Exports:

- source model
- package manifest
- all JSON artifacts
- evidence audit
- imported evidence
- adapter run history
- review markdown
- evidence brief
- source-check register

Purpose:

Give reviewers a reproducible package.

## User Journeys

### Journey 1: Workload Credibility Review

User question:

```text
Can this workload credibly run on this analog chip, what proof exists, what breaks, and what must be built or measured next?
```

Flow:

1. Upload or select a model.
2. Select the target chip profile, Physical AI domain, modality, runtime mode, and calibration assumptions.
3. Build the package.
4. Open the Workload Credibility Answer.
5. Review the platform's direct answer: credible, partial, blocked, or unknown.
6. Inspect proof by category: measured hardware, imported toolkit evidence, simulation, compiler mapping, estimates, source-checked context, and failed adapter attempts.
7. Inspect what breaks: unsupported operators, dynamic attention, Softmax/LayerNorm, analog/digital boundary crossings, sensor/control gaps, calibration/drift gaps, update limits, missing compiler path, missing board trace, or missing task accuracy.
8. Open the ranked next-work list.
9. Export the archive or assign the next engineering work order.

Outcome:

The user gets one decision package instead of scattered reports:

```text
Credible for fixed-weight edge inference.
Partial for transformer projection acceleration.
Blocked for adaptive Physical AI/VLA claims.
Next: import CrossSim sweep, import analog-mlir placement, measure board latency/power, run task accuracy after analog mapping.
```

Platform-owned capabilities used:

- package creation
- graph/operator analysis
- Physical AI domain mapping
- roadmap gate aggregation
- evidence normalization and validation
- safe-claim generation
- gap ranking
- archive export

Toolkit-backed capabilities used:

- AIHWKIT or CrossSim for analog error simulation
- analog-mlir or attention partitioner for compiler mapping
- SST/Golem or ALPINE/gem5-X for simulated runtime when configured
- board, power/thermal, and task metric services when real measurements exist

### Journey 2: Founder Roadmap Triage

User question:

```text
Are we building the right chip roadmap for the Physical AI market we are pitching?
```

Flow:

1. Upload representative customer model.
2. Select target domain and modality.
3. Build package.
4. Open Physical AI roadmap.
5. Review blocked gates.
6. Compare whether the bottleneck is compiler, sensor, control, weight updates, calibration, or transformer partitioning.
7. Export roadmap gap table.

Outcome:

The founder sees whether the roadmap should prioritize compiler support, analog error simulation, board measurement, transformer partitioning, weight update evidence, sensor front-end support, or deterministic control integration.

### Journey 3: ML Systems Engineer Model Bring-Up

User question:

```text
Can this graph reach the analog chip through a real tool path?
```

Flow:

1. Upload ONNX model.
2. Inspect operator mapping.
3. Run compiler probe.
4. Import analog-mlir or compiler placement artifact.
5. Run AIHWKIT or CrossSim simulation.
6. Import task accuracy evidence.
7. Check claim readiness.

Outcome:

The engineer knows which operators map, which fail, what must be rewritten, and whether analog error destroys task accuracy.

### Journey 4: Hardware Engineer Simulation-To-Silicon Validation

User question:

```text
What must we measure or simulate before tape-out or board review?
```

Flow:

1. Build package.
2. Connect AIHWKIT/CrossSim for non-ideality sweeps.
3. Connect analog-mlir/Golem for compiler/runtime graph.
4. Connect SST/Golem or ALPINE/gem5-X for cycle/full-system simulation.
5. Import board runtime and power/thermal evidence when available.
6. Review evidence gaps.

Outcome:

The engineer gets a prioritized validation checklist: array assumptions, parasitics, ADC/DAC limits, memory movement, host overhead, calibration sweep, drift, board trace, and power/thermal traces.

### Journey 5: Transformer/VLA Feasibility Review

User question:

```text
Is this transformer or VLA workload actually analog-friendly, or are we only mapping the easy projection layers?
```

Flow:

1. Upload transformer-like model.
2. Run VLA readiness.
3. Run attention partitioner.
4. Review static projection mapping.
5. Review dynamic QK, Softmax, score-value, LayerNorm, and memory boundaries.
6. Check whether analog pruning or softmax-free rewrite is proposed.
7. Check weight update readiness.

Outcome:

The user sees whether the model is a narrow projection-layer opportunity, a hybrid analog/digital candidate, or blocked for VLA claims.

### Journey 6: Customer Technical Diligence

User question:

```text
What claims are real today?
```

Flow:

1. Open saved package.
2. Review evidence brief.
3. Inspect imported evidence.
4. Check adapter runs and failures.
5. Review claim readiness.
6. Download archive.

Outcome:

The customer can audit exactly what was measured, simulated, estimated, and blocked.

### Journey 7: Investor Diligence

User question:

```text
Is this a credible platform or a demo story?
```

Flow:

1. Review Physical AI roadmap summary.
2. Review source-check register.
3. Review toolkit connection status.
4. Review production claim status.
5. Review roadmap gap priorities.

Outcome:

The investor sees whether the company has an evidence engine for closing claims, not just benchmarks and slides.

## Product Acceptance Criteria

The system is acceptable when:

- every package has a single Physical AI roadmap view
- toolkit connections are explicit and probeable
- AIHWKIT/CrossSim/analog-mlir/SST/ALPINE/attention partition paths are visible as adapter targets
- imported evidence can update specific lab claims only through validation
- transformer/VLA claims are blocked when dynamic attention and Softmax boundaries are unresolved
- fixed-weight inference is separated from update/adaptation readiness
- simulation is never mislabeled as measured board evidence
- source-checked examples never become package evidence
- archive output preserves the full reasoning chain
- frontend users can understand the top gaps without reading raw JSON

## First Build Priorities

1. Keep ONNX import and local model analysis stable.
2. Keep `physical_ai_roadmap` as the aggregate view.
3. Expand adapter registry and playbook around named toolkit families.
4. Add normalized sample templates for AIHWKIT and CrossSim outputs.
5. Add an attention partition artifact.
6. Add simulation provenance labels for SST/Golem and ALPINE/gem5-X.
7. Add frontend toolkit connection rows.
8. Add claim rules that prevent simulation from upgrading measured claims.
9. Add archive coverage for every new artifact.
10. Add smoke tests for missing-toolkit, configured-toolkit, and imported-evidence states.

## Source Links Used For Current Toolkit Framing

- IBM AIHWKIT: https://github.com/IBM/aihwkit
- IBM AIHWKIT paper page: https://research.ibm.com/publications/using-the-ibm-analog-in-memory-hardware-acceleration-kit-for-neural-network-training-and-inference
- Sandia CrossSim: https://github.com/sandialabs/cross-sim
- CrossSim Sandia page: https://cross-sim.sandia.gov/
- analog-mlir: https://github.com/PlatinumCD/analog-mlir
- ALPINE paper: https://arxiv.org/abs/2205.10042
- gem5-X: https://www.epfl.ch/labs/esl/research/full-system-simulation-and-design/gem5-x/
- TxSim paper: https://arxiv.org/html/2002.11151v3
- XBTorch paper: https://arxiv.org/abs/2601.07086
- SynaptogenML: https://github.com/rwth-i6/SynaptogenML
- LIMCA: https://github.com/ACADLab/LIMCA
