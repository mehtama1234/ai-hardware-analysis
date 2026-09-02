# Physical AI Readiness Implementation Spec

Start from the [Connected System Map](connected-system-map.html). This implementation spec uses the same contract: object, constraint, design move, evidence, allowed claim, refused claim, and next handoff.

## Purpose

This spec translates the Physical AI and VLA-era writeup into concrete implementation work.

The current product is an analog in-memory model-fit workbench. It asks:

```text
Can this model run on the analog/digital hardware path?
```

The next product step is a Physical AI edge inference readiness workbench. It should also ask:

```text
Is this the right kind of Physical AI use case for this hardware, and what full-system evidence would prove it?
```

The analog core remains central, but the implementation must judge the wider system:

- domain
- modality
- model type
- transformer/VLA readiness
- analog/digital operator boundary
- weight update pattern
- calibration and drift risk
- compiler ecosystem support
- sensor boundary
- deterministic control boundary
- evidence level

The end-to-end product target is a roadmap workbench, not a set of isolated reports. A user should be able to load one package and see:

```text
the Physical AI domain
  -> model and operator fit
  -> transformer/VLA fit
  -> weight-update fit
  -> calibration/drift fit
  -> deterministic-control boundary
  -> sensor boundary
  -> compiler ecosystem fit
  -> simulation-to-silicon toolkit bridge
  -> transformer attention partitioning
  -> runtime, power, thermal, and task-accuracy evidence
  -> claim readiness
  -> roadmap gaps and next engineering actions
```

Each gate must say what is measured, what is simulated, what is estimated, what is source-checked context, what failed, and what remains blocked. The reports should be separate JSON artifacts for auditability, but the frontend and archive should make them read as one Physical AI analog-chip roadmap.

## Implementation Principle

Do not add this as marketing text.

Add it as generated artifacts, frontend panels, package exports, and smoke-test coverage.

Each new report should follow the existing product pattern:

```text
input settings + model analysis + runtime/evidence state
  -> plain-language report
  -> structured JSON artifact
  -> frontend panel
  -> archive file
  -> smoke-test check
```

## New Backend Artifacts

### 0. Simulation-To-Silicon Toolkit Bridge

Artifact keys:

```text
adapter_registry
connection_playbook
compiler_ecosystem_readiness
physical_ai_roadmap
```

Purpose:

Turn generic "connect a simulator/compiler" language into concrete adapter targets for AIMC toolkits.

Detailed product rationale, backend/frontend capabilities, and user journeys are specified in `simulation-to-silicon-first-principles-spec.md`.

Adapter targets:

- `sim.aihwkit`: AIHWKIT-style PyTorch hardware-aware simulation for ADC/DAC limits, programming noise, drift, IR drop, and write/update non-idealities.
- `sim.crosssim`: CrossSim-style crossbar accuracy simulation for bit slicing, read/programming noise, parasitic wire resistance, and ADC range policy.
- `compiler.analog-mlir-golem`: analog-mlir-style lowering into analog execution IR, static weight isolation, task graph assembly, and Golem/SST runtime graph output.
- `system.sst-golem`: cycle/system co-simulation for CPU dispatch, synchronization, memory movement, and simulated analog-array execution.
- `system.alpine-gem5x`: full-system AIMC simulation for CPU integration, custom ISA/library dispatch, memory hierarchy, and OS/runtime overhead.
- `compiler.attention-partitioner`: transformer partitioning for static projection/FFN weights, dynamic attention, Softmax/LayerNorm, score-value matmul, analog pruning, and rewrite candidates.

Rules:

- AIHWKIT and CrossSim outputs normalize to `analog_error_simulation` unless they also include task metrics, in which case task accuracy must still be imported separately.
- analog-mlir and attention partitioner outputs normalize to `compiler_mapping`; they do not prove latency, energy, or accuracy by themselves.
- SST/Golem and ALPINE/gem5-X outputs normalize to `board_runtime` only as simulated runtime evidence unless a measured board source is attached.
- toolkit examples and paper metrics are source-checked context, not package evidence.
- transformer/VLA readiness must stay blocked when only static projection mapping exists and dynamic attention/Softmax boundaries remain unmeasured.

### 1. Physical AI Map

Module:

```text
backend/physical_ai_map.py
```

Artifact key:

```text
physical_ai_map
```

Endpoint:

```text
GET /deployment-packages/{package_id}/physical-ai-map
```

Archive file:

```text
physical-ai-map.json
```

Purpose:

Show where the selected workload fits in the Physical AI landscape.

Inputs:

- package report
- selected target profile
- selected modality
- workload fit matrix
- system boundary report
- measurement evidence

Output should include:

- selected domain
- selected domain label
- analog fit
- main evidence gap
- domain rows
- sensors
- typical tasks
- where edge compute matters
- where analog/in-memory compute may help
- where it gets harder
- evidence needed
- claims to avoid
- cross-domain rules

Acceptance:

- output includes mobility, ambient hardware, industrial systems, infrastructure, agriculture, defense/aerospace, sensory hardware, and robotics/VLA
- selected domain changes based on modality and target profile
- output avoids unsourced vendor claims

### 2. VLA / Transformer Readiness

Module:

```text
backend/vla_transformer_readiness.py
```

Artifact key:

```text
vla_readiness
```

Endpoint:

```text
GET /deployment-packages/{package_id}/vla-readiness
```

Archive file:

```text
vla-readiness.json
```

Purpose:

Show whether the model and selected hardware path look ready for transformer-class or VLA-style workloads.

Inputs:

- operator analysis
- quantization report
- runtime profile
- system boundary report
- package report

Output should inspect:

- matrix-heavy layers
- attention-like patterns
- softmax
- layer normalization
- GeLU or activation-heavy regions
- reshape/transpose movement
- sequence-like dimensions
- memory-heavy operators
- digital-required operators
- analog/digital boundary count
- fallback count

Output should explain:

- what can plausibly map to analog
- what likely remains digital
- whether the model is CNN-like, MLP-like, transformer-like, or unknown
- whether the current result supports a VLA-ready claim
- what evidence is missing

Plain-language rule:

```text
Analog MAC efficiency does not prove VLA readiness. VLA readiness depends on operator coverage, memory movement, attention support, compiler mapping, accuracy, latency, and jitter.
```

Acceptance:

- report flags softmax/layernorm/attention-like operators as digital or risk-heavy
- report separates matrix-heavy analog opportunity from transformer glue work
- report gives a safe claim level such as `not_vla_ready`, `early_transformer_fit`, or `hybrid_vla_candidate`

### 3. Weight Update Readiness

Module:

```text
backend/weight_update_readiness.py
```

Artifact key:

```text
weight_update_readiness
```

Endpoint:

```text
GET /deployment-packages/{package_id}/weight-update-readiness
```

Archive file:

```text
weight-update-readiness.json
```

Purpose:

Show whether the hardware story assumes fixed weights or can support frequent adaptation.

This is a roadmap gate, not a marketing note. The report should make one distinction impossible to miss:

```text
low-power fixed-weight inference is not the same thing as adaptive Physical AI readiness
```

The artifact should answer:

```text
Can this chip support the weight-update pattern this workload needs, or should the claim stop at fixed-weight inference?
```

Inputs:

- package report
- target profile
- modality
- project context
- hardware profile assumptions
- calibration profile
- VLA readiness
- Physical AI domain map
- measurement evidence state
- imported evidence records, when available

Initial implementation may use explicit assumptions rather than measured hardware.

Output should include:

- assumed update pattern: static, occasional, per-customer, per-device, frequent
- update readiness class: `fixed_weight_ready`, `periodic_update_candidate`, `adapter_update_candidate`, or `adaptive_physical_ai_blocked`
- update scope: full model, selected layers, embedding table, action head, LoRA or adapter block, calibration constants, or no supported update path
- memory update risk
- write latency evidence status
- write energy evidence status
- endurance evidence status
- write voltage evidence status
- retention evidence status
- post-update accuracy evidence status
- recalibration requirement
- rollback requirement
- thermal impact of repeated writes
- whether update energy is counted separately from inference energy
- whether the current compiler/runtime can identify writable weights or adapter blocks
- claim boundary
- evidence needed before stronger claims

Classification rules:

- fixed wake-word, simple camera, or industrial monitoring workloads default to fixed or occasional update unless project settings say otherwise
- robotics, VLA-adjacent, tactile/event/multimodal, or changing sensor-layout workloads default to higher update risk
- frequent local adaptation is blocked unless measured write latency, write energy, endurance, recalibration, rollback, and post-update accuracy evidence are present
- adapter-update claims require evidence that the compiler and hardware can isolate writable adapter blocks without rewriting the full model
- update assumptions must not change claim readiness by themselves

Acceptance:

- default output says update behavior is not measured unless evidence exists
- adaptive robotics/VLA use cases are marked higher risk than fixed wake-word or camera classifiers
- report says fixed-weight inference efficiency does not prove adaptive-model readiness
- report blocks adaptive Physical AI claims when update measurements are missing
- report separates inference energy from update energy
- report explains what must be measured before claiming on-device adaptation
- archive includes the update-readiness class, evidence gaps, and claim boundary

### 4. Calibration And Drift Readiness

Module:

```text
backend/calibration_drift_readiness.py
```

Artifact key:

```text
calibration_drift_readiness
```

Endpoint:

```text
GET /deployment-packages/{package_id}/calibration-drift-readiness
```

Archive file:

```text
calibration-drift-readiness.json
```

Purpose:

Make calibration, drift, and fallback behavior a first-class gate.

Inputs:

- calibration profile
- package report
- runtime profile
- measurement evidence
- target profile

Output should include:

- temperature range
- voltage range
- calibration provenance
- drift risks
- aging risks
- weak-cell or weak-row status when available
- recalibration schedule status
- failure behavior
- evidence needed to upgrade the claim

Acceptance:

- report blocks safety or production claims when drift evidence is missing
- report explains that analog calibration is part of reliability, not a side detail
- report distinguishes simulated profile, replay fixture, prototype evidence, and measured hardware

### 5. Control Boundary

Module:

```text
backend/control_boundary.py
```

Artifact key:

```text
control_boundary
```

Endpoint:

```text
GET /deployment-packages/{package_id}/control-boundary
```

Archive file:

```text
control-boundary.json
```

Purpose:

Show that the inference chip is not the motor controller or full safety controller.

Inputs:

- selected domain
- target profile
- modality
- runtime profile
- system boundary report

Output should include:

- inference role
- deterministic control role
- safety monitor role
- host/runtime role
- expected handoff signal
- latency and jitter evidence status
- what the analog chip should not claim

Acceptance:

- robotics, mobility, defense, and agriculture use cases show explicit control/safety boundary
- report says neural inference can support action but does not replace deterministic control
- report asks for bounded latency and jitter evidence

Current implementation status:

- backend module implemented in `backend/control_boundary.py`
- saved package endpoint implemented at `GET /deployment-packages/{package_id}/control-boundary`
- frontend panel implemented as `Inference Is Not Control`
- deployment archive writes `control-boundary.json`
- smoke coverage checks frontend markers, endpoint response, project-run artifact, saved artifact, and archive file

### 6. Compiler Ecosystem Readiness

Module:

```text
backend/compiler_ecosystem_readiness.py
```

Artifact key:

```text
compiler_ecosystem_readiness
```

Endpoint:

```text
GET /deployment-packages/{package_id}/compiler-ecosystem-readiness
```

Archive file:

```text
compiler-ecosystem-readiness.json
```

Purpose:

Show whether the product can meet developers where they work.

Inputs:

- adapter registry
- external connector contract
- connection playbook
- operator analysis
- package report

Output should include:

- ONNX status
- PyTorch export status
- JAX/XLA status
- simulator path status
- compiler mapping status
- unsupported operator reporting
- rewrite support
- profiling support
- evidence import support
- zero-touch score
- explainable mapping score

Acceptance:

- report treats ONNX support as current first path
- report marks PyTorch and JAX/XLA as roadmap or connector work unless implemented
- report says zero-touch is the goal but explainable mapping is required
- report links compiler gaps back to adoption risk

Current implementation status:

- backend module implemented in `backend/compiler_ecosystem_readiness.py`
- saved package endpoint implemented at `GET /deployment-packages/{package_id}/compiler-ecosystem-readiness`
- frontend panel implemented as `Can Developers Reach The Chip?`
- deployment archive writes `compiler-ecosystem-readiness.json`
- smoke coverage checks frontend markers, endpoint response, project-run artifact, saved artifact, and archive file

### 7. Sensor Boundary Readiness

Module:

```text
backend/sensor_boundary_readiness.py
```

Artifact key:

```text
sensor_boundary_readiness
```

Endpoint:

```text
GET /deployment-packages/{package_id}/sensor-boundary-readiness
```

Archive file:

```text
sensor-boundary-readiness.json
```

Purpose:

State where physical signals become model-ready tensors and who pays the energy, latency, and calibration cost.

Inputs:

- selected domain
- modality
- target profile
- system boundary report
- runtime profile

Output should include:

- expected sensors
- likely raw signal type
- preprocessing owner
- AFE status
- event-stream status
- tactile/force status
- timestamp/synchronization status
- energy accounting gap
- evidence needed

Acceptance:

- audio, health, industrial, tactile, and event-vision use cases show sensor-front-end questions
- report does not count inference-only energy as full sensor-to-output energy
- report supports two boundary choices: raw-sensor-adjacent chip or digital-tensor accelerator

Current implementation status:

- backend module implemented in `backend/sensor_boundary_readiness.py`
- saved package endpoint implemented at `GET /deployment-packages/{package_id}/sensor-boundary-readiness`
- frontend panel implemented as `Signal To Tensor`
- deployment archive writes `sensor-boundary-readiness.json`
- smoke coverage checks frontend markers, endpoint response, project-run artifact, saved artifact, and archive file

## Backend Integration

Update `backend/main.py` so package creation builds and persists the new artifacts.

`build_artifact_bundle` should add:

```text
physical_ai_map
vla_readiness
weight_update_readiness
calibration_drift_readiness
control_boundary
compiler_ecosystem_readiness
sensor_boundary_readiness
```

`persist_artifact_bundle` should:

- preserve these artifacts
- add saved artifact links
- include them in archive generation
- recompute derived artifacts when saved evidence changes if needed

Saved package artifact links should include:

```json
{
  "physical_ai_map": "/deployment-packages/{package_id}/physical-ai-map",
  "vla_readiness": "/deployment-packages/{package_id}/vla-readiness",
  "weight_update_readiness": "/deployment-packages/{package_id}/weight-update-readiness",
  "calibration_drift_readiness": "/deployment-packages/{package_id}/calibration-drift-readiness",
  "control_boundary": "/deployment-packages/{package_id}/control-boundary",
  "compiler_ecosystem_readiness": "/deployment-packages/{package_id}/compiler-ecosystem-readiness",
  "sensor_boundary_readiness": "/deployment-packages/{package_id}/sensor-boundary-readiness"
}
```

## Frontend Implementation

Add panels after `Workload fit` and before lower-level connector panels.

Panels:

- `Physical AI Map`
- `VLA / Transformer Readiness`
- `Weight Update Readiness`
- `Calibration & Drift Gate`
- `Control Boundary`
- `Compiler Ecosystem Readiness`
- `Sensor Boundary`

Each panel should use the same simple pattern:

- short summary sentence
- key/value facts
- evidence gaps
- what helps
- what gets harder
- what not to claim

Do not add vendor examples to the frontend until they are source-checked.

## Archive Implementation

Update `build_deployment_archive` to include:

```text
physical-ai-map.json
vla-readiness.json
weight-update-readiness.json
calibration-drift-readiness.json
control-boundary.json
compiler-ecosystem-readiness.json
sensor-boundary-readiness.json
```

Update the archive `README.txt` contents list so reviewers understand these are Physical AI readiness reports, not measured hardware proof.

## Smoke Tests

Update `backend/scripts/smoke_end_to_end.py`.

Frontend checks:

- `physicalAiMapSummary`
- `/physical-ai-map`
- `vlaReadinessSummary`
- `/vla-readiness`
- `weightUpdateSummary`
- `/weight-update-readiness`
- `calibrationDriftSummary`
- `/calibration-drift-readiness`
- `controlBoundarySummary`
- `/control-boundary`
- `compilerEcosystemSummary`
- `/compiler-ecosystem-readiness`
- `sensorBoundarySummary`
- `/sensor-boundary-readiness`

Backend checks:

- each endpoint returns the expected `result_type`
- each saved package contains each artifact
- archive contains every new JSON file

Content checks:

- `physical_ai_map` includes all required domains
- `vla_readiness` includes transformer/operator risk language
- `weight_update_readiness` does not claim measured update support by default
- `calibration_drift_readiness` blocks production/safety claims without drift evidence
- `control_boundary` separates inference from deterministic control
- `compiler_ecosystem_readiness` marks PyTorch and JAX/XLA as roadmap unless implemented
- `sensor_boundary_readiness` identifies preprocessing and energy-accounting gaps

## Implementation Order

1. Implement `physical_ai_map.py`.
2. Add frontend `Physical AI Map` panel.
3. Add archive and smoke coverage for that first artifact.
4. Implement `vla_transformer_readiness.py`.
5. Add frontend `VLA / Transformer Readiness` panel.
6. Implement weight update, calibration drift, and control boundary reports.
7. Add archive and smoke coverage for weight update, calibration drift, and control boundary.
8. Implement compiler ecosystem report.
9. Add archive and smoke coverage for compiler ecosystem.
10. Implement sensor boundary report.
11. Add archive and smoke coverage for sensor boundary.
12. Only after the conceptual reports work, source-check vendor examples and decide whether to add cited case studies. Initial source-check records live in `source-check-register.md`.

## Non-Goals

Do not implement a real VLA compiler in this milestone.

Do not claim support for Gemini Robotics, Rho-alpha, or any current vendor model until source-checked and technically validated.

Do not claim frequent on-chip weight updates until write energy, latency, endurance, and recalibration evidence exists.

Do not claim robotic control support from inference latency alone.

Do not use sensor-interface claims unless AFE, event-stream, tactile, synchronization, and preprocessing costs are counted.

## Definition Of Done

This implementation is done when the app can answer, in one package:

```text
What Physical AI domain is this workload closest to?
Is this model transformer/VLA-like or simpler?
Which parts are analog opportunities and which stay digital?
Does the update pattern match the hardware memory story?
Is calibration and drift evidence strong enough?
Where does deterministic control sit?
Can developers reach the chip from normal model frameworks?
Where do raw physical signals become tensors?
What evidence is still missing before we make a strong claim?
```
