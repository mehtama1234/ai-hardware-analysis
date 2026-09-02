# Frontend And Backend Architecture

## Product Goal

The software product should help a customer answer one practical question:

Can my trained model run on this analog in-memory AI hardware with the accuracy, latency, energy, and reliability my device needs?

The chip may be the technical center, but the software has to turn the chip into a usable product. The software should make model conversion, quantization, operator mapping, calibration, runtime execution, debugging, profiling, and deployment visible.

## Connected-System Contract

The frontend and backend should implement the contract described in `connected-system-map.html`.

- The **frontend** should show the object being judged, the constraint acting on it, the evidence available, and the claim state.
- The **backend** should produce and store the artifacts that make that claim state auditable.
- The **hardware lab** should export normalized evidence that the backend can import without changing the frontend contract.
- The **claim engine** should keep local, simulated, RTL, OpenLane, board-measured, power-measured, silicon-backed, and production-backed evidence levels separate.

The current package `pkg-e931662a01293df2` exercises this contract through hardware placement, hardware-lab evidence import, claim readiness, and a cross-repo proof. `C1` and `C4` are supported for the bounded local setup. `C2` and `C3` remain needs review until measured board runtime and measured power evidence exist. Production readiness remains blocked.

## First Principle

The software exists because the analog core is not a general computer. It is good at specific work, mainly repeated matrix math near stored weights. Other work may need digital logic or a host processor.

So the software has to answer these questions:

- What does the model contain?
- Which operators can run on the analog path?
- Which operators must run digitally?
- How much accuracy is lost after quantization and analog error?
- How often does data cross the analog/digital boundary?
- How much latency and energy does each part cost?
- Does the final result satisfy the target device constraints?

## High-Level Architecture

```text
Frontend
  -> Project workspace
  -> Physical AI readiness map
  -> Model intake
  -> VLA / transformer readiness
  -> Compatibility report
  -> Quantization review
  -> Analog/digital mapping view
  -> Weight update readiness
  -> Calibration status
  -> Calibration and drift gate
  -> Control boundary
  -> Compiler ecosystem readiness
  -> Sensor boundary
  -> Profiling dashboard
  -> Deployment package view

Backend
  -> Model registry
  -> Model importer
  -> Physical AI map service
  -> Operator analyzer
  -> VLA / transformer readiness service
  -> Quantization service
  -> Mapping planner
  -> Weight update readiness service
  -> Calibration service
  -> Calibration and drift readiness service
  -> Control boundary service
  -> Compiler ecosystem readiness service
  -> Sensor boundary readiness service
  -> Runtime orchestrator
  -> Profiling and metrics store
  -> Deployment packager
```

## Physical AI Readiness Layer

The workbench must grow beyond a narrow analog model-fit checker.

The analog core is still the center of the hardware story, but Physical AI workloads add questions the current model-fit flow does not fully answer:

- What real-world domain is this workload for?
- Is the model CNN-like, MLP-like, transformer-like, or VLA-like?
- Does the workload assume fixed weights or frequent adaptation?
- Is calibration strong enough for temperature, voltage, aging, and drift?
- Where does deterministic control and safety sit outside the inference chip?
- Can developers reach the chip from ONNX, PyTorch export, JAX/XLA, or simulator pipelines?
- Where do raw sensor signals become model-ready tensors?

These questions should be implemented as first-class backend artifacts and frontend panels, not as static prose.

The implementation source is [physical-ai-readiness-implementation-spec.md](physical-ai-readiness-implementation-spec.md).

## Frontend Architecture

The frontend should not start as a marketing site. It should start as a workbench for model evaluation.

### 1. Project Workspace

The user creates a project for a target workload.

The project should capture:

- model name
- model type
- target device class
- modality
- task type
- primary failure cost
- target latency
- target energy per inference
- target accuracy
- temperature or operating range if known
- intended deployment environment

This matters because "edge AI" is not one market. A wearable and a robot do not have the same constraints.

### 2. Model Intake View

The user imports a model from PyTorch, TensorFlow, ONNX, or a pre-exported graph.

The view should show:

- model file
- input shape
- output shape
- parameter count
- operator list
- unsupported operators
- estimated memory footprint

The purpose is simple: before discussing chip performance, the system must know what the model is.

### 3. Compatibility Report

This is the first major user-facing output.

It should explain:

- which layers are likely analog-friendly
- which layers need digital fallback
- which operators are unsupported
- where conversion may happen
- where memory movement may dominate
- whether the model is a good, medium, or poor fit

This report should use plain language. For example:

```text
Most matrix multiplication layers can map to the analog array.
LayerNorm and Softmax need digital support.
The model may pay conversion cost around attention blocks.
```

### 3a. Model-Fit Report Frontend

Yes, the analysis should be shown directly on the frontend. The backend computes the operator analysis, but the frontend turns it into a decision page a customer can understand.

The page should answer four questions immediately:

- Can this model run on the hardware?
- Which parts benefit from analog in-memory compute?
- Which parts need digital fallback?
- What are the likely accuracy, latency, energy, and integration risks?

The first screen should show a compact verdict:

```text
Hardware fit: Medium
Analog coverage: 71% of compute-heavy operators
Digital fallback: 8 operators
Main risk: attention block conversion cost
Next step: run quantization sensitivity analysis
```

Below that, the frontend should show a layer-by-layer table. Each row should be one model operator or fused layer. The user should see the operator type, tensor shape, estimated cost, planned execution location, fallback reason if any, and risk level.

Example:

```text
Layer                  Type        Placement       Risk
encoder.matmul.1       MatMul      analog core     low
encoder.layernorm.1    LayerNorm   digital path    medium
attention.softmax      Softmax     digital path    medium
classifier.dense       MatMul      analog core     low
```

The page should also show an analog/digital boundary map. This does not need to be a complex graph in the first version. A simple sequence view is enough:

```text
input
  -> digital preprocessing
  -> analog matmul block
  -> ADC boundary
  -> digital normalization
  -> DAC boundary
  -> analog matmul block
  -> digital output
```

This matters because the boundary is where energy can be lost. If the model crosses between analog and digital too often, the chip may still work, but the efficiency story becomes weaker.

The frontend should include a "why" explanation for each decision. If an operator runs digitally, the UI should say why in plain language:

```text
LayerNorm is placed on the digital path because this hardware target does not support it in the analog array.
This creates one analog-to-digital boundary before the layer and one digital-to-analog boundary after it.
```

The report should end with recommended next actions:

```text
Run quantization sensitivity.
Try replacing unsupported GELU with supported approximation.
Keep attention softmax on digital path.
Measure ADC/DAC overhead around transformer blocks.
```

This makes the frontend useful before the customer ever deploys to real silicon. It lets them understand whether their model is a good fit, what has to change, and what should be measured next.

### 4. Quantization Review

The frontend should show how the model changes when moved from training precision to hardware precision.

This view must be modality-aware. It should not use the same interpretation for audio, vision, robotics, industrial sensing, health signals, and language models. The backend may use a common quantization engine, but the frontend must show the metric that matters for the chosen task.

It should show:

- baseline accuracy
- quantized accuracy
- per-layer sensitivity
- weights that need protection
- suggested precision per layer
- expected accuracy risk
- selected modality
- selected task metric
- primary failure cost
- calibration dataset status
- whether the result is estimated, simulated, or measured

This view is important because analog hardware only works well when the model can tolerate the numeric format.

Examples of modality-specific display:

```text
audio wake-word
  -> false accept rate, false reject rate, noisy-input sensitivity

vision classifier
  -> top-1 accuracy, per-class drops, first-conv and classifier-head sensitivity

object detection
  -> mAP, recall, box quality, confidence threshold movement

robotics perception
  -> latency, output jitter, worst-case error, safety margin

industrial anomaly
  -> anomaly recall, missed-fault rate, threshold drift

health signal
  -> sensitivity, specificity, missed events, false alarms

edge LLM
  -> perplexity, task score, token latency, attention and output-logit sensitivity
```

### 5. Analog/Digital Mapping View

This should be one of the most important views.

It should show the model as a graph or layer list with each part labeled:

```text
analog core
digital accelerator
host CPU
unsupported
```

The user should be able to see:

- where the analog path starts and ends
- where ADCs and DACs are used
- where data moves between memory regions
- where fallback happens
- which layers dominate latency
- which layers dominate energy

This view answers the question: where does analog actually help?

### 6. Calibration Status

The frontend should show whether the hardware is calibrated for the current model and device condition.

It should show:

- calibration version
- chip or board identity
- temperature and voltage range covered
- calibration age
- failing or weak memory regions
- expected accuracy impact

Analog systems need this because the real chip can drift away from the ideal model.

### 7. Profiling Dashboard

The dashboard should not only show TOPS/W.

It should show:

- energy per inference
- latency per inference
- accuracy after quantization and calibration
- analog compute time
- digital fallback time
- ADC/DAC overhead
- memory movement cost
- idle power
- sustained performance under heat

This is the product-level proof.

### 8. Deployment Package View

After the model passes checks, the frontend should show the deployment package.

It should include:

- model artifact
- quantization metadata
- mapping plan
- calibration profile
- runtime configuration
- supported device target
- version history

The goal is to make deployment repeatable.

## Backend Architecture

The backend should be built around explicit artifacts. Each stage should produce a saved artifact, not just a temporary result. That makes debugging and comparison possible.

External compiler, simulator, analog, digital, and board tools should be hidden behind backend adapters. The frontend should call stable product APIs and render normalized artifacts. It should not parse raw SPICE output, compiler logs, RTL simulation output, or board telemetry directly.

### 1. Model Registry

Stores uploaded models, versions, metadata, and target constraints.

Core entities:

- project
- model
- model version
- target device profile
- workload profile
- accuracy target
- latency target
- energy target

### 2. Model Importer

Reads the model and converts it into an internal graph.

Responsibilities:

- parse PyTorch export, TensorFlow, or ONNX
- extract operators
- infer shapes
- detect constants and weights
- normalize graph representation
- flag unsupported structures

The importer should not optimize first. It should first describe the model truthfully.

### 3. Operator Analyzer

Classifies each operator by hardware fit.

Example categories:

- analog-friendly
- digital-required
- fallback-required
- unsupported
- needs rewrite
- needs precision review

This creates the first hardware-fit report.

### 4. Quantization Service

Converts weights and activations into hardware-supported formats.

Responsibilities:

- choose default precision
- run calibration data through the model
- measure accuracy impact
- identify sensitive layers
- mark weights needing protection
- produce quantization metadata
- select modality adapter
- select task metric adapter
- track failure-cost preference
- label result provenance as estimated, simulated, or measured

For analog hardware, this service should include error-aware quantization, not only normal low-bit quantization.

The modality adapter defines what "good enough" means. For a wake-word model, false accepts and false rejects matter more than generic accuracy. For industrial anomaly detection, missed faults can matter more than false alarms. For robotics, jitter and latency misses can matter more than average accuracy. For an edge LLM, token latency and quality degradation matter more than image-style top-1 accuracy.

### 5. Mapping Planner

Decides where each part of the model runs.

Responsibilities:

- map matrix-heavy layers to analog arrays
- keep unsupported or sensitive operators digital
- estimate ADC/DAC crossings
- estimate memory movement
- choose tiling or splitting strategy
- produce execution graph

The planner is where hardware architecture becomes software policy.

### 6. Calibration Service

Matches the model plan to real chip behavior.

Responsibilities:

- read chip characterization data
- apply per-chip correction factors
- detect weak or unreliable cells
- adjust references or scale values
- decide if recalibration is needed
- attach calibration profile to deployment package

This service turns "ideal hardware behavior" into "this physical chip's behavior."

### 7. Runtime Orchestrator

Runs inference according to the prepared execution plan.

Responsibilities:

- load model package
- schedule analog and digital operations
- move inputs and outputs
- manage memory buffers
- call fallback paths
- collect runtime traces
- enforce latency or power modes

This should be designed for edge deployment, not only cloud testing.

### 8. Profiling And Metrics Store

Stores measurement results.

Metrics should include:

- accuracy
- latency
- energy per inference
- analog time
- digital time
- ADC/DAC overhead
- memory traffic
- idle power
- temperature
- voltage
- fallback count
- operator-level timing

This makes claims auditable.

### 9. Deployment Packager

Creates the final artifact for a customer device.

Package contents:

- model graph
- quantized weights
- mapping plan
- calibration profile
- runtime config
- device profile
- compatibility report
- profiling report

The package should be versioned so the customer can reproduce results.

## External Tool Adapter Strategy

Start with local estimated analysis. Add external tools later through adapters.

```text
frontend
  -> backend API
    -> model importer
    -> quantization adapter
    -> compiler adapter
    -> simulator adapter
    -> calibration adapter
    -> board runtime adapter
    -> metrics adapter
```

Likely future connections:

- ONNX Runtime, PyTorch export, TensorFlow, and TFLite for model handling
- ONNX Runtime quantization, PyTorch quantization, and custom analog-aware quantizers
- MLIR, TVM, IREE, or a custom hardware compiler
- SPICE, Spectre, HSPICE, ngspice, device variation models, and ADC/DAC models
- Verilog/SystemVerilog simulation, Verilator, cocotb, synthesis reports, timing reports, and power reports
- board telemetry, calibration firmware, power monitors, temperature sensors, debug paths, and runtime traces

Every result should include provenance:

```text
mock
estimated
simulated
compiler_report
prototype_board
production_board
customer_device
```

This prevents a mock estimate from looking like measured silicon.

## Suggested Service Boundaries

```text
api-gateway
  -> authentication, project APIs, upload APIs

model-service
  -> model registry, import, graph extraction

analysis-service
  -> operator support, model-fit reports, sensitivity analysis

quantization-service
  -> quantization runs, accuracy checks, protected-weight decisions

mapping-service
  -> analog/digital placement, tiling, conversion estimation

calibration-service
  -> chip profiles, correction data, recalibration decisions

runtime-service
  -> execute prepared model on simulator, board, or chip

metrics-service
  -> traces, profiling, energy, latency, accuracy, reports

artifact-service
  -> deployment packages and versioned outputs
```

For a first version, these do not need to be separate deployed services. They can be modules inside one backend. The important point is to keep the boundaries clear.

## Data Model

Core tables or collections:

```text
projects
models
model_versions
target_devices
workload_profiles
operator_reports
quantization_runs
mapping_plans
chip_profiles
calibration_profiles
runtime_runs
metric_traces
deployment_packages
```

Important relationships:

```text
project -> model_versions
project -> workload_profile
model_version -> operator_report
model_version -> quantization_runs
quantization_run -> mapping_plans
mapping_plan -> calibration_profile
calibration_profile -> runtime_runs
runtime_run -> metric_traces
runtime_run -> deployment_package
```

## First Milestone

Build the model-fit report first.

The first milestone should do this:

```text
1. Import an ONNX model.
2. Extract the operator graph.
3. Classify operators as analog-friendly, digital-required, fallback-required, or unsupported.
4. Estimate where analog/digital boundaries would occur.
5. Produce a plain-language report.
```

Why this first? Because it answers the earliest customer question:

Can my model even use this hardware?

This can be built before hardware access is complete. Later, the same workflow can add quantization, calibration, profiling, and deployment.

## What Not To Build First

Do not start with a generic dashboard. A dashboard without real model analysis will look polished but will not answer the hard product question.

Do not start with a full compiler. A complete compiler is too large for the first step. Start with graph import, operator classification, and a clear report.

Do not start with production deployment tooling. Deployment matters, but only after the model-fit, quantization, mapping, and calibration loop is understood.

## Clean Interview Framing

The software architecture should be framed like this:

The hardware advantage only matters if customers can reach it with their own models. I would design the software around the full model-to-inference path: import the model, analyze operator support, quantize it for the hardware, map layers across analog and digital paths, calibrate against real chip behavior, run inference, and measure accuracy, latency, energy, and reliability. The first product milestone should be a model-fit report because it tells a customer whether their workload is a good match before asking them to rewrite or deploy anything.
