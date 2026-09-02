# End-To-End Build Goal

## Goal

Build a model-fit workbench for analog in-memory AI inference hardware.

The product should take a trained model, analyze whether it fits the hardware, show where analog compute helps, show where digital fallback is needed, estimate the risks, and produce a clear report that helps a customer decide whether to continue toward deployment.

The goal is not to build a generic dashboard. The goal is to build the software path that makes the hardware usable.

## Connected-System Contract

This goal now uses the same contract as `connected-system-map.html`.

- **Object:** customer workload, model graph, hardware placement, analog error evidence, governor row, RTL trace, OpenLane report, imported evidence, board trace, power trace, and final claim.
- **Constraint:** analog error, converter cost, tile size, memory movement, fallback, calibration, timing, power, thermal behavior, update behavior, unsupported operations, and evidence provenance.
- **Design move:** place work in analog, keep work digital, split around converter boundaries, retry, fall back, calibrate, measure, import, or block.
- **Evidence:** named JSON artifact, backend endpoint, simulator output, RTL check, synthesis report, OpenLane context, board trace, meter trace, task result, or package archive.
- **Claim boundary:** supported claims must name their evidence; unsupported measured-board, measured-power, calibrated-silicon, analog-macro, production, or safety claims must remain blocked.

The current live proof slice is package `pkg-e931662a01293df2`. It proves a local model-to-placement-to-lab-to-claim loop. It does not prove measured board latency, measured energy, calibrated silicon behavior, analog macro integration, package reliability, or production readiness.

```text
trained model
  -> import
  -> inspect operators
  -> classify hardware fit
  -> quantize
  -> map analog and digital execution
  -> estimate boundary and memory costs
  -> calibrate against chip behavior
  -> profile real or simulated inference
  -> package deployment artifacts
  -> explain the result to the customer
```

## Why This Matters

An analog core by itself is not a product. A customer needs to know whether their model can run on the chip and whether the claimed hardware benefit survives the full system.

The hard questions are:

- Does the model contain operators the analog core can accelerate?
- Which layers must stay digital?
- How often does data cross ADC and DAC boundaries?
- Does quantization preserve accuracy?
- Are sensitive weights protected?
- Does calibration keep the chip reliable across temperature, voltage, and manufacturing variation?
- Is energy per completed inference actually better after counting memory movement, fallback, runtime, and idle cost?

This workbench should make those questions visible.

## Primary User

The primary user is an ML systems engineer, hardware customer engineer, or solutions engineer evaluating whether a model is a good fit for the chip.

They are not trying to read a marketing claim. They are trying to answer:

```text
Can I run my model on this hardware, and what will break first?
```

## End-To-End Product Flow

### 1. Create Project

The user creates a project and chooses a target device class.

Examples:

- wearable always-on audio
- smart camera vision
- robot sensor fusion
- industrial sensor monitoring

The project captures target constraints:

- accuracy target
- latency target
- energy per inference target
- temperature range
- voltage range
- memory limit
- model update frequency

### 2. Import Model

The user imports a model from ONNX first.

Later formats can include PyTorch export and TensorFlow.

The importer extracts:

- model name
- input and output shapes
- operator graph
- parameter count
- weight tensors
- activation shapes
- unsupported graph structures

First milestone should support ONNX because it is a practical interchange format.

### 3. Analyze Operator Fit

The backend classifies each operator.

Categories:

- analog-friendly
- digital-required
- fallback-required
- unsupported
- needs rewrite
- needs precision review

The first frontend report should show this as a layer table with plain-language reasons.

Example:

```text
MatMul -> analog core -> dense matrix work with reused weights
LayerNorm -> digital path -> not supported in analog array
Softmax -> digital path -> nonlinear attention operation
DepthwiseConv -> fallback -> low reuse on this target
```

### 4. Build The Analog/Digital Mapping Plan

The system decides where each layer should run.

The mapping plan should show:

- analog layers
- digital layers
- fallback layers
- ADC boundaries
- DAC boundaries
- data movement between regions
- estimated cost per boundary

This is central because analog compute only helps if the analog/digital crossings do not erase the energy benefit.

### 5. Quantization And Sensitivity

The system converts the model into hardware-supported number formats and measures accuracy impact.

Quantization sensitivity must be modality-aware. The backend can share one quantization engine, but the scoring and acceptance criteria must change by use case. A wake-word model, smart-camera detector, robotics perception model, industrial anomaly detector, health wearable model, and edge LLM do not fail in the same way.

It should support:

- baseline accuracy tracking
- INT8 trial
- INT4 trial
- per-layer sensitivity
- sensitive weight detection
- protected-weight recommendations
- analog-error simulation or injection
- modality-specific metrics
- task-specific failure-cost settings
- calibration dataset requirements by modality

The key output is not just a smaller model. The key output is a model that still gives correct answers under the hardware's numeric limits.

The project should capture these quantization inputs:

- modality: audio, vision, robotics, industrial sensor, health signal, or language model
- task type: classification, detection, anomaly detection, control support, or sequence generation
- primary failure cost: false positive, false negative, latency miss, unstable output, or quality degradation
- task metric: false accept/reject, top-1 accuracy, mAP, recall, jitter, sensitivity/specificity, perplexity, or token latency

Examples:

```text
wearable audio
  -> track false accepts, false rejects, noisy-input behavior

vision classifier
  -> track top-1 accuracy, per-class drops, first-conv and classifier sensitivity

object detection
  -> track mAP, recall, box quality, confidence threshold movement

robotics perception
  -> track latency, output jitter, worst-case error, safety margin

industrial anomaly detection
  -> track anomaly recall, false negatives, threshold drift on rare events

health wearable
  -> track sensitivity, specificity, missed events, false alarms, signal quality

edge LLM
  -> track perplexity, task quality, token latency, attention and output-logit sensitivity
```

### 6. Calibration Integration

The system connects model execution to real chip behavior.

Calibration should include:

- chip or board profile
- temperature range
- voltage range
- weak memory rows or cells
- correction factors
- reference settings
- calibration version
- expected accuracy impact

In the first backend version, calibration can use mocked chip profiles. Later, it should connect to board measurements.

### 7. Runtime Execution

The prepared model runs on a simulator first, then on hardware when available.

The runtime should:

- load the model package
- schedule analog and digital operations
- manage data buffers
- call fallback operators
- apply calibration
- collect traces
- return model outputs

The runtime is where the architecture becomes a real system.

Current implementation status:

- The backend has a first simulated runtime profile endpoint.
- The frontend can call it after ONNX import.
- The report shows completed-inference latency, completed-inference energy, host overhead, idle energy, bottlenecks, and whether the target is met.
- The backend and frontend can compare the simulated analog path with an estimated digital baseline using completed-inference latency and energy.
- The backend and frontend can generate an evidence gate report that marks each requirement as passed, estimated, blocked, or missing.
- The backend and frontend can generate a plain-language review report for interview or customer discussion.
- The artifact is explicitly marked `provenance: simulated` and `confidence: low`.

This is not a real inference engine yet. It is the first product-shaped version of the runtime layer: it makes the full-system accounting visible before external simulator or board connections exist.

### 8. Profiling And Measurement

The product must show product-level proof, not only TOPS/W.

Metrics:

- accuracy
- latency per inference
- energy per inference
- estimated analog result compared with a digital baseline
- analog compute time
- digital fallback time
- ADC/DAC overhead
- memory movement
- host/runtime overhead
- idle power
- thermal behavior

The key metric is:

```text
energy per completed inference at a fixed accuracy and latency target
```

### 9. Recommendations

The system should tell the user what to try next.

Examples:

- keep LayerNorm on digital path
- protect attention projection weights
- try INT4 only on feed-forward layers
- reduce analog/digital crossings around attention
- replace unsupported operator with supported approximation
- run wider temperature calibration

Recommendations must point to specific layers and specific reasons.

### 10. Deployment Package

When the model passes checks, the system creates a deployment package.

Package contents:

- imported model graph
- quantized weights
- mapping plan
- calibration profile
- runtime configuration
- operator support report
- profiling report
- target device profile

The package must be versioned so results can be reproduced.

Current implementation status:

- The backend emits a package-readiness artifact after ONNX import.
- The frontend shows the package ID, schema version, readiness stage, manifest, blockers, and hand-off actions.
- The frontend can download an evaluation archive that includes the source ONNX and generated JSON artifacts.
- Generated package artifacts are persisted by package ID for later retrieval.
- Uploaded model records are persisted and reloaded after backend restart.
- Projects persist target profile, modality, calibration profile, runtime mode, imported models, and package IDs.
- Generated package and review artifacts include project ID and project name when a project is attached.
- The package report is explicit that no hardware executable binary is emitted in this prototype.
- The archive includes the estimated digital baseline comparison so reviewers can see what was counted and excluded.
- The archive includes the adapter registry so reviewers can see which external tools were local, configured, or not connected.
- The archive includes the evidence gate report so reviewers can see the safe claim and remaining proof gaps.
- The archive includes a Markdown review report with what to say, what not to overclaim, hard parts, and next evidence.
- The claim level distinguishes unsupported operators, analysis-only packages, simulated evaluation packages, prototype evidence packages, and deployment candidates.

This closes the first loop from model import to package decision and review archive. The next hard step is replacing estimates with real artifacts: real quantized weights, real compiler mapping, real simulator traces, and eventually board measurements.

## How The Research Guide Maps To Product Requirements

The research guide at `../index.html` should directly shape what the product builds and what the product refuses to overclaim. Each conceptual point becomes a software requirement.

### 1. Analog Is A Tradeoff, Not A Universal Replacement

Research idea:

Analog compute can save energy for repeated matrix math, but digital compute remains better for precision, flexibility, and broad programmability.

Product requirement:

The workbench must never report a single generic "analog is better" result. It must classify fit by workload and layer.

Frontend evidence:

- analog-friendly layers
- digital-required layers
- fallback layers
- unsupported layers
- placement reason for each layer

Backend requirement:

The operator analyzer must treat hardware support as a capability profile, not a yes/no chip claim. The same model may score differently on wearable, camera, robotics, or industrial profiles.

Acceptance:

The report can explain why one model is a high fit and another is only medium or poor, even if both are "edge AI" models.

### 2. Data Movement Is The Core Problem

Research idea:

The main energy cost is often moving weights, activations, and intermediate results, not only doing multiplication.

Product requirement:

The workbench must estimate and display data movement risk.

Frontend evidence:

- boundary map
- memory movement estimate
- analog/digital crossing count
- layer-level movement warnings

Backend requirement:

The mapping planner must produce a movement-aware execution plan. It should estimate where data moves between analog arrays, digital support logic, SRAM, DRAM, host memory, and output buffers.

Acceptance:

The report can identify cases where analog compute is efficient but total model execution may still be limited by movement.

### 3. ADC And DAC Cost Must Be Counted

Research idea:

Analog compute needs conversion at the analog/digital boundary. ADCs and DACs can reduce or erase the energy benefit if used too often.

Product requirement:

The workbench must show every conversion boundary and include conversion cost in energy estimates.

Frontend evidence:

- visible ADC nodes
- visible DAC nodes
- conversion cost in energy breakdown
- boundary warnings around attention, normalization, softmax, or fallback paths

Backend requirement:

The boundary analyzer must count conversion crossings and attach estimated latency and energy cost to each crossing.

Acceptance:

The product cannot mark a model as a strong fit unless conversion overhead is included in the fit score.

### 4. TOPS/W Is Not Product Proof

Research idea:

TOPS/W is useful, but it may only measure a compute macro. Product proof is energy per completed inference at a fixed accuracy and latency target.

Product requirement:

The profiler must make energy per inference the primary metric.

Frontend evidence:

- energy per inference
- latency per inference
- accuracy after quantization and calibration
- energy breakdown by analog compute, conversion, memory movement, fallback, and runtime

Backend requirement:

The metrics service must store trace-level measurements or estimates. It must separate compute macro cost from full-system cost.

Acceptance:

Every performance report must show what was counted and whether the number is estimated, simulated, or measured on hardware.

### 5. Quantization And Numeric Error Are Product Risks

Research idea:

Analog hardware uses approximate physical signals. Models may tolerate some error, but not all layers and weights are equally tolerant.

Product requirement:

The workbench must show quantization sensitivity and analog-error risk.

Frontend evidence:

- baseline accuracy
- quantized accuracy
- analog-error estimate
- sensitive layers
- protected-weight recommendations
- precision recommendation per layer

Backend requirement:

The quantization runner must support at least INT8 first, with a path for INT4 and analog-error injection. It should identify layers where lower precision causes unacceptable accuracy loss.

The quantization runner must use a modality adapter. The adapter defines the metric that matters, the likely sensitive regions, the calibration dataset shape, and the failure mode that should be treated as most serious.

Acceptance:

The user can see which parts of the model are safe to approximate and which parts should stay higher precision or digital.

Additional acceptance:

The same numeric accuracy drop can produce different recommendations depending on modality. For example, a small average accuracy drop may be acceptable for a simple image classifier but unacceptable for an industrial anomaly detector if rare fault recall drops.

### 6. Calibration Is A First-Class Workflow

Research idea:

Analog chip behavior changes with manufacturing variation, temperature, voltage, and aging. Calibration is how the system keeps model behavior close enough to expected behavior.

Product requirement:

The product must attach every hardware-backed result to a calibration profile.

Frontend evidence:

- chip or board ID
- calibration version
- covered temperature range
- covered voltage range
- weak rows or cells
- correction factors
- expected accuracy impact

Backend requirement:

The calibration service must store chip profiles and expose them to mapping, quantization, runtime, and report generation.

Acceptance:

The product can distinguish an ideal estimate, a simulator result, and a result tied to a specific calibrated board.

### 7. Prototype Silicon Is Not Production Readiness

Research idea:

A prototype shows that the idea reached silicon. Production requires yield, repeatability, calibration cost, packaging, software support, customer integration, and real operating validation.

Product requirement:

The workbench should track readiness level for each result.

Frontend evidence:

- result source: estimated, simulated, prototype board, production board
- calibration status
- board count or chip count when available
- operating condition coverage
- warning when claims are based on limited data

Backend requirement:

Metrics and calibration records must include provenance. The system should know when a result came from a mock profile, simulator, lab board, or production-like device.

Acceptance:

The report does not present prototype-board results as production proof unless repeatability and operating-condition coverage are available.

### 8. Edge AI Is Not One Market

Research idea:

Wearables, robots, smart cameras, and industrial sensors have different duty cycles, latency needs, battery limits, safety expectations, model sizes, and cost targets.

Product requirement:

Every project must have a target device profile.

Frontend evidence:

- target device selector
- accuracy, latency, energy, memory, temperature, and update constraints
- market-specific warnings
- fit score tied to the selected profile

Backend requirement:

The hardware support rules and fit scoring must use the target profile. A wearable always-on workload should not be scored the same way as a robot perception workload.

Acceptance:

Changing the target device profile can change the fit score, recommendations, and risk explanation.

### 9. Software Support Is Part Of The Hardware Product

Research idea:

Customers do not only buy a circuit. They need model import, quantization, mapping, calibration, runtime, debugging, profiling, supported-operator clarity, and deployment tools.

Product requirement:

The workbench must expose the whole model-to-chip path, not just the final inference number.

Frontend evidence:

- model import status
- operator support report
- quantization review
- mapping view
- calibration view
- profiling view
- deployment package summary

Backend requirement:

Each stage must produce a saved artifact that can be inspected and compared.

Acceptance:

The user can trace a deployment package back to the source model, quantization run, mapping plan, calibration profile, and profiling result.

### 10. Paper Lessons Become Product Checks

The paper deep dives also map to concrete checks:

```text
isca-2025-098
  -> protect sensitive weights, do not force all weights into the same low-precision analog path

date-2025-193
  -> treat MRAM variation and calibration as measurable system concerns

isscc-2025-089
  -> support multiple precision modes or explain why a layer needs a specific format

isscc-2025-100
  -> distinguish macro-level results from end-to-end DNN inference

dac-2025-376
  -> map transformer attention carefully, not only dense matrix layers

dac-2025-380
  -> include ADC area, energy, and latency in product-level estimates

dac-2024-370
  -> route sensitive operations through safer digital or higher-precision paths

iccad-2025-056
  -> model analog error impact on neural-network accuracy, not only circuit error

dac-2025-130
  -> adapt placement to workload demand and target power mode

dac-2025-127
  -> treat edge LLM inference as memory-heavy and not automatically solved by analog MAC

fccm-2025-053
  -> use automation for design exploration, but require simulation and silicon validation
```

Acceptance:

The product requirements should be traceable back to these lessons. If a feature does not help explain fit, accuracy, energy, calibration, or deployment readiness, it should not be part of the first build.

## Architecture Deliverables

### Frontend

Build the model-fit workbench.

Required views:

- project setup
- model intake
- hardware-fit verdict
- layer placement table
- analog/digital boundary map
- quantization review
- calibration view
- profiling view
- recommendations
- deployment package summary

The frontend should use real API-shaped data from day one, even if the first data is mocked.

The frontend should also show provenance and confidence for every result. A local estimate, simulator result, compiler report, prototype-board run, and production-board run should not look equivalent.

### Backend

Build the first backend as a modular service.

Required modules:

- model registry
- ONNX importer
- operator analyzer
- hardware support rules engine
- mapping planner
- quantization runner
- calibration profile service
- runtime runner
- metrics store
- deployment packager

These can start as one backend process with clear module boundaries.

External tool connections should be added through adapters, not hardwired into the UI or core analysis flow. See [external-tool-integration-spec.md](external-tool-integration-spec.md). The detailed first-principles product specification for AIHWKIT, CrossSim, analog-mlir/Golem/SST, ALPINE/gem5-X, attention partitioning, and related simulation-to-silicon toolkits lives in [simulation-to-silicon-first-principles-spec.md](simulation-to-silicon-first-principles-spec.md).

### API

Required first APIs:

```text
POST /models/import
GET  /models/{model_id}/graph
POST /models/{model_id}/analyze-fit
GET  /analyses/{analysis_id}/summary
GET  /analyses/{analysis_id}/operator-report
GET  /analyses/{analysis_id}/boundary-map
POST /analyses/{analysis_id}/quantize
GET  /quantization-runs/{run_id}
GET  /devices/{device_id}/calibration
POST /runtime-runs
GET  /runtime-runs/{run_id}/profile
POST /deployment-packages
```

## Build Milestones

### Milestone 1: Interactive Mock Workbench

Status: started.

Deliver:

- static frontend
- mock API JSON
- project switching
- layer filtering
- clickable inspector
- boundary map
- quantization chart
- energy breakdown
- recommendations

Acceptance:

- user can switch between at least three workload profiles
- UI updates from JSON, not hardcoded markup
- layer selection updates inspector
- report explains placement decisions in plain language

### Milestone 2: Real ONNX Import

Deliver:

- backend endpoint to upload or register ONNX model
- graph extraction
- operator list
- shape extraction
- parameter count
- model summary

Acceptance:

- user can import an ONNX file
- frontend shows real model name, operators, shapes, and parameter count
- unsupported import errors are readable

### Milestone 3: Operator Fit Engine

Status: first pass built.

Deliver:

- hardware capability profile
- operator classification rules
- analog/digital/fallback labels
- placement reasons
- first fit score

Acceptance:

- each operator gets a placement label
- each placement has a plain-language reason
- frontend table is generated from real backend analysis

### Milestone 4: Boundary And Cost Estimation

Status: first pass built.

Deliver:

- analog/digital boundary detection
- ADC/DAC crossing count
- rough latency estimate
- rough energy estimate
- memory movement estimate

Acceptance:

- frontend shows boundary map from backend
- report identifies the highest-risk boundary region
- energy estimate separates analog compute, conversion, memory movement, fallback, and runtime

### Milestone 5: Quantization Sensitivity

Status: first estimated pass built.

Deliver:

- INT8 quantization path
- optional INT4 trial
- calibration dataset input
- accuracy comparison
- per-layer sensitivity report
- modality adapter
- task metric adapter
- failure-cost setting
- precision recommendation per layer
- protected-weight or protected-layer recommendation

Acceptance:

- report shows baseline accuracy and quantized accuracy
- sensitive layers are marked
- recommendations identify where lower precision is safe or risky
- user must choose or confirm modality and task type before interpreting the result
- report shows the task metric that matters for that modality
- report labels first-pass results as estimated until real calibration data is run

### Milestone 6: Calibration Profiles

Status: first profile-selection pass built.

Deliver:

- mocked chip profiles first
- real board profile interface later
- weak-cell or weak-row metadata
- correction-factor metadata
- temperature and voltage coverage

Acceptance:

- deployment analysis is tied to a specific device profile
- frontend shows calibration status and expected accuracy impact

### Milestone 7: Runtime And Profiling

Deliver:

- simulator-backed runtime first
- hardware-backed runtime later
- trace capture
- latency and energy reporting
- operator-level profiling

Acceptance:

- user can run a prepared model against a runtime target
- frontend shows measured or simulated energy per inference
- profiling identifies bottlenecks

### Milestone 8: Deployment Package

Deliver:

- versioned deployment artifact
- model graph
- quantized weights
- mapping plan
- calibration profile
- runtime config
- report export

Acceptance:

- user can export a reproducible package
- package records the model version, target device, calibration profile, and analysis version

Status: evaluation-archive pass built.

Current acceptance:

- user can generate a reproducible package-readiness report from an imported ONNX model
- user can download a ZIP evaluation archive for review
- user can retrieve a saved package report, review report, and archive by package ID
- user can list imported models and saved packages after backend restart
- user can create and list backend projects and see which model/package IDs belong to the project
- user can update a project's target profile, modality, calibration profile, runtime mode, and name before creating another evaluation run
- user can run one project evaluation that produces analysis, quantization, runtime, baseline, measurement-evidence, evidence, review, decision, rewrite, what-if, rewrite-plan, rewrite-work-order, adapter, and package artifacts from the saved project context
- user can list saved evaluation runs globally and by project, and retrieve one run by run ID
- each saved run records model ID, package ID, target profile, modality, calibration profile, runtime mode, latency, energy, energy ratio, fit, evidence status, and safe claim
- user can compare saved runs and see deltas for latency, energy, analog coverage, fallback count, energy efficiency, fit, and claim status
- user can select saved projects, models, packages, and runs from the frontend registry instead of copying IDs manually
- user can reopen a saved run by loading its persisted analysis, quantization, runtime, baseline, package, Physical AI readiness, source-check, measurement-evidence, evidence, review, decision, rewrite, what-if, rewrite-plan, rewrite-work-order, and adapter artifacts
- user can inspect a selected run in one focused panel with settings, metrics, evidence counts, artifact links, and comparison deltas when available
- user can inspect a measurement evidence contract that separates configured adapters from actual compiler, simulator, board, power, thermal, and task-accuracy artifacts
- user can import a normalized external evidence artifact and attach it to a package or run without treating other missing sources as measured
- user can batch import sample normalized evidence artifacts for all required sources to demonstrate lab-claim progression
- user can recalculate claim readiness so each lab claim is supported only by its required imported evidence while production readiness remains blocked
- user can get a decision report that says `good fit`, `needs rewrite`, `needs measurement`, or `not a fit yet`, with reasons, next actions, and claims to avoid
- user can get rewrite suggestions for specific layers, boundary crossings, protected analog layers, and low analog coverage, with expected impact and verification steps
- user can run a rewrite what-if estimate that shows simulated changes to coverage, fallback, boundaries, latency, energy, and decision before editing the actual model
- user can build a rewrite plan that turns selected suggestions into graph, compiler, runtime, validation, and evidence steps
- user can build a rewrite work order that turns the plan into owner-facing tasks, done criteria, acceptance gates, and evidence attachments
- downloaded review/archive artifacts remain self-describing with project context
- report records model ID, model name, target device, calibration profile, modality, runtime mode, package schema version, and package ID
- report lists manifest items, blockers, safe claim level, and next evidence to collect
- archive includes `manifest.json`, `package-readiness.json`, `analysis.json`, `quantization-report.json`, `runtime-profile.json`, `baseline-comparison.json`, `workload-fit.json`, `system-boundary.json`, `physical-ai-map.json`, `vla-readiness.json`, `weight-update-readiness.json`, `calibration-drift-readiness.json`, `control-boundary.json`, `sensor-boundary-readiness.json`, `research-guide.json`, `concept-glossary.json`, `source-check-register.json`, `toolchain-readiness.json`, `compiler-ecosystem-readiness.json`, `connection-playbook.json`, `measurement-evidence.json`, `adapter-registry.json`, `evidence-gates.json`, `claim-readiness.json`, `evidence-audit.json`, `evidence-brief.json`, `evidence-brief.md`, `interview-brief.json`, `interview-brief.md`, `interview-drill.json`, `decision-report.json`, `rewrite-suggestions.json`, `rewrite-what-if.json`, `rewrite-plan.json`, `rewrite-work-order.json`, `review-report.json`, `review-report.md`, `imported-evidence/index.json`, imported evidence JSON files, and `source-model.onnx`

Remaining acceptance:

- include real quantized weights
- include compiler-produced mapping artifacts
- include saved runtime traces and report export
- emit a hardware executable package once compiler/runtime adapters exist

### Milestone 9: Physical AI Domain Map

Status: implemented end to end. Current state audit is in [current-state-audit.md](current-state-audit.md), concept spec is in [physical-ai-domain-map-spec.md](physical-ai-domain-map-spec.md), implementation spec is in [physical-ai-readiness-implementation-spec.md](physical-ai-readiness-implementation-spec.md), and source-checked example policy is in [source-check-register.md](source-check-register.md).

Deliver:

- a backend `physical_ai_map` artifact
- a saved package endpoint at `/deployment-packages/{package_id}/physical-ai-map`
- a `physical-ai-map.json` file in the exported archive
- a frontend `Physical AI Map` panel after workload fit
- domain rows for mobility, ambient hardware, industrial systems, infrastructure, agriculture, defense/aerospace, sensory hardware, and robotics/VLA systems
- simple explanations for sensors, model tasks, duty cycle, power/heat pressure, analog/in-memory fit, hard parts, evidence needed, and claims to avoid
- source-check separation for current company, product, and paper examples
- implemented VLA readiness, weight updates, calibration drift, control boundary, compiler ecosystem, sensor boundary, and source-check register reports

Implemented artifacts:

- `physical_ai_map`: places the selected workload in the larger Physical AI landscape
- `vla_readiness`: explains transformer/VLA fit, analog opportunity, digital support needs, and claim limits
- `weight_update_readiness`: separates fixed-weight inference from field adaptation and on-chip update claims
- `calibration_drift_readiness`: covers temperature, voltage, drift, aging, recalibration, and failure-behavior evidence
- `control_boundary`: separates neural inference from deterministic control, safety monitors, and actuator handoff
- `sensor_boundary_readiness`: explains signal-to-tensor ownership, AFE/event/tactile/sync status, and sensor-to-output energy gaps
- `compiler_ecosystem_readiness`: marks ONNX as the first path and PyTorch/JAX/XLA as roadmap unless implemented
- `source_check_register`: exposes checked examples, official source links, allowed-use text, and do-not-claim boundaries

Acceptance:

- user can see where the selected workload fits in the larger Physical AI landscape
- user can tell which domain-specific metric matters before discussing analog acceleration
- user can see why edge inference matters for the selected domain
- user can see where analog or in-memory compute may help and where it may not
- user can see which evidence is required before making a strong domain claim
- frontend and archive do not present unsourced current vendor claims as facts
- user can see guarded source-checked examples without implying measured support, compatibility, partnership, or production readiness

### Milestone 10: Evidence-Backed Physical AI Roadmap Workbench

Status: partially implemented through generated readiness artifacts, package archives, source-check policy, evidence imports, and adapter-run audit trails. The next step is to make each roadmap gate evidence-backed enough to guide engineering and investor/customer claims.

Purpose:

The workbench should become the operating system for deciding whether an analog inference chip startup has a real Physical AI path or only a narrow fixed-model demo. It should not only answer whether one ONNX model can run. It should answer:

```text
Is this workload a real fit for the analog chip, what full-system roadmap gaps remain, and what evidence would prove or block each claim?
```

The output should be useful to four audiences at once:

- the founder deciding product roadmap priorities
- the ML systems engineer trying to bring a model onto the chip
- the hardware engineer deciding what must be measured on silicon or board
- the investor or customer asking which claims are real, estimated, blocked, or still roadmap

End-to-end scope:

- Physical AI domain fit: classify the workload across mobility, ambient hardware, industrial systems, infrastructure, agriculture, defense/aerospace, sensory hardware, robotics/VLA, or simpler edge inference, then state the domain metric and failure mode that matter.
- Model and operator fit: identify analog-friendly layers, digital-required operators, unsupported operators, fallback paths, boundary crossings, memory movement, ADC/DAC costs, and rewrite opportunities.
- Transformer and VLA readiness: separate simple CNN/MLP edge models from transformer, multimodal, VLA-adjacent, attention-heavy, or language/action workloads; explain why analog MAC efficiency alone does not prove VLA readiness.
- Weight update readiness: decide whether the chip is credible for fixed weights, occasional updates, adapter updates, or frequent adaptive Physical AI.
- Calibration and drift readiness: test whether accuracy survives temperature, voltage, aging, device variation, recalibration, failed calibration, and fallback behavior.
- Deterministic control boundary: name where neural inference stops and real-time control, safety monitors, actuator timing, interlocks, and motor logic take over.
- Sensor boundary: state where raw physical signals become model-ready tensors, who owns AFE/event/tactile/sync/preprocessing cost, and whether sensor-to-output latency and energy are counted.
- Compiler ecosystem readiness: show whether ONNX, PyTorch, JAX/XLA, simulator-generated models, custom kernels, and compiler-produced analog/digital placement are implemented, connected, blocked, or roadmap.
- Simulation-to-silicon bridge readiness: show whether AIHWKIT, CrossSim, analog-mlir/Golem/SST, ALPINE/gem5-X, or equivalent toolkits are connected well enough to turn model graphs into physical error models, compiler placement, cycle simulation, and full-system runtime evidence.
- Transformer partitioning readiness: identify static projection and FFN weights that may be analog-friendly, dynamic QK/score-value attention work that likely stays digital or needs specialized mixed-signal hardware, Softmax/LayerNorm bottlenecks, analog-pruning candidates, and rewrite options such as softmax-free attention.
- External evidence connectors: integrate compiler mapping, analog/error simulation, board runtime, power/thermal, and task-accuracy services through auditable adapters.
- Evidence and claim discipline: separate measured hardware, imported lab evidence, replay fixtures, local simulation, estimates, source-checked examples, failed connector attempts, and assumptions.
- Roadmap generation: turn every blocked claim into engineering actions, owners, evidence needed, acceptance gates, and safe wording.

The final product should make this conversation concrete:

```text
Here is the physical system.
Here is the model.
Here is what the analog chip can run.
Here is what stays digital.
Here is what must be measured.
Here is what failed.
Here is what claim is safe today.
Here is the roadmap gap that must close next.
```

Deliver:

- a single roadmap-grade package view that brings together `physical_ai_map`, `vla_readiness`, `weight_update_readiness`, `calibration_drift_readiness`, `control_boundary`, `sensor_boundary_readiness`, `compiler_ecosystem_readiness`, measurement evidence, claim readiness, evidence audit, adapter runs, connector status, rewrite plan, and work order
- per-gate status classes such as `supported`, `needs measurement`, `roadmap connector`, `blocked`, and `do not claim`
- per-gate evidence requirements that distinguish required measured artifacts from assumptions or source-checked examples
- a roadmap gap table that ranks the next engineering work by claim impact, evidence gap, implementation risk, and customer/investor importance
- a simulation-to-silicon adapter matrix that names the intended toolkit path: AIHWKIT-style differentiable HWA, CrossSim-style crossbar accuracy simulation, analog-mlir/SST-Golem compiler/runtime co-simulation, ALPINE/gem5-X full-system simulation, and transformer attention partitioning
- archive output that preserves the complete reasoning chain: model, package settings, estimates, imported evidence, failed connector attempts, source-check register, roadmap gate statuses, and safe claims
- frontend panels that make the roadmap readable without hiding the evidence details
- smoke coverage proving that unsupported gates remain blocked and do not inherit confidence from unrelated estimates

Acceptance:

- a user can load a model/package and see one coherent Physical AI roadmap, not disconnected reports
- every major gate says what is known, what is assumed, what is measured, what failed, and what must be done next
- safe claims are generated from evidence state, not from market narrative
- failed configured external services are preserved as audit trail and do not trigger local fallback confidence
- source-checked examples are visible as context but cannot become compatibility, performance, partnership, or production-readiness evidence
- imported evidence can move specific lab claims only when it matches the normalized contract for the required source
- production readiness remains blocked until compiler, board, power/thermal, accuracy, calibration, control, and reliability evidence satisfy the claim contract
- the exported archive is strong enough for review by an engineering lead, customer technical team, or diligence team

Roadmap gates:

- `domain_fit`: Is this the right Physical AI domain for the chip, and what metric matters?
- `model_fit`: Which graph regions can run on analog, and what breaks the hardware story?
- `vla_transformer_fit`: Is this simple edge inference or transformer/VLA-adjacent work?
- `weight_update_fit`: Can the chip support the needed update pattern?
- `calibration_drift_fit`: Does the chip remain reliable across real physical conditions?
- `control_boundary_fit`: Is real-time control and safety clearly outside or integrated with inference?
- `sensor_boundary_fit`: Are raw-signal, AFE, event, tactile, sync, and preprocessing costs counted?
- `compiler_fit`: Can real customer graphs reach the chip through ONNX/PyTorch/JAX/XLA/simulator paths?
- `simulation_to_silicon_fit`: Is there a credible bridge from model graph to hardware-aware training/simulation, physical crossbar error, compiler lowering, cycle simulation, and full-system runtime?
- `attention_partition_fit`: For transformer/VLA workloads, which operations are static analog candidates, which are dynamic digital work, and where do Softmax/conversion/update costs block the claim?
- `runtime_power_fit`: Are latency, jitter, energy, thermal, and host overhead measured or only estimated?
- `task_accuracy_fit`: Does the task metric survive analog mapping, quantization, and drift?
- `evidence_integrity`: Are measured, simulated, replayed, estimated, failed, and source-checked artifacts separated?

### Milestone 10B: Simulation-To-Silicon Toolkit Bridge

Status: adapter targets named; next step is to normalize real outputs from each toolkit family.

Purpose:

The workbench must not stop at "compiler needed" or "simulator needed." It should name the actual bridge from a model to physical AIMC evidence:

```text
Can this package move from graph analysis to hardware-aware simulation, compiler placement, cycle simulation, and full-system evidence without hand-wavy gaps?
```

Toolkit families to support as adapter targets:

- `sim.aihwkit`: PyTorch hardware-aware simulation for analog noise, converter precision, IR drop, drift, and write/update behavior.
- `sim.crosssim`: crossbar accuracy simulation for bit slicing, programming/read noise, ADC range, and parasitic wire resistance.
- `compiler.analog-mlir-golem`: MLIR-style analog lowering, static weight isolation, task graph construction, and Golem/SST runtime graph generation.
- `system.sst-golem`: cycle-level CPU/accelerator co-simulation for dispatch, synchronization, memory movement, and simulated analog execution.
- `system.alpine-gem5x`: full-system AIMC simulation for CPU integration, custom ISA/library dispatch, memory hierarchy, Linux/runtime overhead, and model execution.
- `compiler.attention-partitioner`: transformer/VLA partitioning that separates static projections and FFN weights from dynamic attention, Softmax, LayerNorm, score-value, and analog-pruning opportunities.

Deliver:

- adapter registry entries and probe contracts for each toolkit family
- normalized artifact contracts that keep compiler mapping, analog error simulation, board/runtime simulation, power/thermal, and task accuracy separate
- frontend and archive visibility that shows which toolkit path is connected, missing, blocked, or only conceptual
- transformer-specific partition output that identifies static analog candidates, dynamic digital work, Softmax/conversion bottlenecks, and rewrite candidates
- source-check discipline that treats toolkit examples as context until this package imports normalized evidence

Acceptance:

- a user can see whether AIHWKIT/CrossSim-style analog simulation is available and what physical non-idealities it covers
- a user can see whether analog-mlir/SST-Golem or ALPINE/gem5-X style co-simulation is connected and whether its result is simulated runtime, not measured board evidence
- transformer/VLA claims are blocked unless the report separates static weight-stationary analog work from dynamic attention and digital non-linear work
- simulation output cannot upgrade production readiness unless normalized evidence, measured corroboration, and claim rules allow it

### Milestone 10A: Weight Update Readiness As A Roadmap Gate

Status: first artifact implemented; next step is to make it evidence-backed.

Purpose:

The workbench must not treat model weights as a one-time setup detail. For Physical AI, robotics, VLA-adjacent, industrial, and customer-adaptive deployments, the model may need to change after the device ships. A useful analog inference chip roadmap must therefore answer a harder question:

```text
Can this chip support the update pattern this physical system needs, or is it only credible for fixed-weight inference?
```

Why this matters:

- analog IMC efficiency is strongest when weights are stable and reused
- adaptive Physical AI may require customer fine-tunes, body-specific adapters, sensor-layout changes, task updates, or periodic field refreshes
- slow, high-energy, high-voltage, low-endurance, or recalibration-heavy writes can erase the practical value of low-power inference
- a chip can be excellent for static wake-word, camera, or sensor models while still being a poor fit for fast-adapting VLA or robotics workloads
- investors and customers need to know whether "on-device adaptation" is real, limited to small adapters, or still a roadmap claim

Deliver:

- a stronger `weight_update_readiness` artifact that classifies the update mode as `fixed_weight_ready`, `periodic_update_candidate`, `adapter_update_candidate`, or `adaptive_physical_ai_blocked`
- explicit update-scope fields: full model, selected layers, embedding table, action head, LoRA or adapter block, calibration constants, or no supported update path
- explicit update-frequency assumptions: factory-only, rare service update, per-customer update, periodic fleet update, per-device personalization, or frequent local adaptation
- required evidence fields for write latency, write energy, write endurance, write voltage, post-write accuracy, post-write recalibration, retention, rollback, and thermal impact
- a model and domain risk assessment that raises risk for robotics/VLA, tactile/event/multimodal systems, changing sensor layouts, and customer-specific deployment environments
- a plain-language claim boundary explaining whether the package supports fixed inference only, occasional update claims, adapter-update claims, or no adaptive claim
- frontend copy that makes fixed-weight efficiency visibly different from adaptive-model readiness
- archive and package persistence so reviewers can audit which update assumptions were used
- smoke coverage that proves adaptive domains do not silently inherit fixed-weight claims

Acceptance:

- a user can see whether the selected workload is likely static, occasionally updated, adapter-updated, or frequently adaptive
- a user can see whether the current evidence supports the required update pattern
- the report blocks adaptive Physical AI claims when write latency, write energy, endurance, recalibration, rollback, or post-update accuracy evidence is missing
- the report separates inference energy from update energy and does not let a low inference number hide expensive reprogramming
- the report explains whether the chip can update only small adapter blocks or must rewrite the full model
- the report explains what must be measured before claiming on-device adaptation
- the frontend and archive keep `weight_update_readiness` separate from measured runtime evidence unless real update measurements are imported
- claim readiness does not move because of an update-roadmap assumption; it only moves when normalized evidence is validated and imported

Evidence needed before stronger claims:

- compiler or runtime artifact showing which weights or adapter blocks are actually writable on the target hardware
- measured write-latency trace for the selected update scope
- measured write-energy or power trace for the selected update scope
- endurance data for repeated updates under the relevant memory technology
- retention data after update
- post-update accuracy comparison against the task metric
- recalibration time and accuracy impact after writing
- rollback or safe-fallback proof when an update fails validation
- thermal behavior during repeated writes

Safe claim levels:

- `fixed_weight_ready`: the package supports static or rarely changed weights; no adaptive Physical AI claim.
- `periodic_update_candidate`: occasional updates may be plausible, but require measured write cost, recalibration, and rollback evidence.
- `adapter_update_candidate`: small task adapters or heads may be plausible without rewriting the full model, if compiler and hardware evidence identify the writable scope.
- `adaptive_physical_ai_blocked`: frequent local adaptation, body transfer, or VLA-style update claims are blocked until update measurements exist.

## Non-Goals For The First Build

Do not build a full compiler first.

Do not build a generic metrics dashboard first.

Do not try to support every model format first.

Do not claim hardware performance until the measurement path counts conversion, memory movement, fallback, runtime, and thermal behavior.

Do not hide unsupported operators. The product should make hardware limits visible.

## Definition Of Done

The end-to-end system is done when a user can:

1. Create a project with target device constraints.
2. Import a real ONNX model.
3. See a real operator graph and model summary.
4. Get analog, digital, fallback, and unsupported placement labels.
5. Understand why each placement was chosen.
6. See where ADC/DAC boundaries occur.
7. Run quantization sensitivity.
8. Attach a calibration profile.
9. Run simulated or real inference.
10. See accuracy, latency, energy per inference, and risk.
11. Export a versioned deployment package and report.

## Clean One-Sentence Goal

Build a model-fit workbench that turns a trained model into an evidence-backed analog in-memory inference deployment plan, showing where the hardware helps, where it does not, what accuracy and energy risks exist, and what the customer should do next.
