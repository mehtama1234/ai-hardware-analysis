# Frontend Design For The Model-Fit Workbench

## Design Goal

The frontend should help a hardware customer answer one question quickly:

Can this model run well on this analog in-memory AI chip?

The page should not feel like a generic analytics dashboard. It should feel like an engineering workbench: upload a model, inspect the fit, understand the risks, and decide what to do next.

## First User Flow

```text
Create project
  -> choose target device profile
  -> import model
  -> run model-fit analysis
  -> inspect analog/digital mapping
  -> run quantization sensitivity
  -> review estimated accuracy, latency, energy, and risk
  -> export report or deployment package
```

The first version should stop at the model-fit report if hardware runtime is not ready yet. That is still valuable because it tells the customer whether their workload is likely to benefit.

## Primary Screen Layout

Use one main workbench screen with four zones.

```text
------------------------------------------------------------
Top bar: Project / Model / Target Device / Run Analysis
------------------------------------------------------------
Left rail: Workflow steps

  1. Model
  2. Physical AI Map
  3. VLA Readiness
  4. Operator Fit
  5. Analog Boundary
  6. Quantization
  7. Calibration
  8. Control Boundary
  9. Profiling
  10. Package

Main canvas:
  current analysis view

Right inspector:
  selected layer details, risks, recommendations
------------------------------------------------------------
Bottom strip:
  accuracy target | latency target | energy target | status
------------------------------------------------------------
```

This layout works because the user needs both a whole-model view and per-layer detail. The main canvas shows the system view. The right inspector explains the selected item.

## Screen 1: Model Intake

The first screen should ask for only what is needed.

Fields:

- model file or model registry path
- model format: ONNX, PyTorch export, TensorFlow
- input shape
- target device profile
- modality
- task type
- primary failure cost
- target accuracy
- target latency
- target energy per inference
- expected operating range if known

After upload, show a simple summary:

```text
Model: keyword_detector_v3.onnx
Parameters: 3.8M
Operators: 94
Inputs: audio_window[1, 16000]
Target: wearable always-on audio
```

Do not ask the user to think about analog placement yet. First show what the model is.

## Screen 2: Hardware-Fit Verdict

Before the hardware-fit verdict, the frontend should show the Physical AI context. The user needs to know what kind of physical system this workload represents before interpreting analog coverage.

## Screen 2A: Physical AI Map

Show where the selected project sits in the wider Physical AI landscape.

The panel should answer:

- What domain is this closest to?
- What sensors are likely involved?
- What task is the model doing?
- Why does edge inference matter here?
- Where could analog or in-memory compute help?
- What gets harder in this domain?
- What evidence is needed before making a strong claim?

Example:

```text
Selected domain: Ambient hardware
Why edge matters: always-on local inference, low idle power, fast wake response
Analog fit: possible
Main evidence gap: false wake / missed wake behavior plus full duty-cycle energy
```

Do not put unsourced vendor examples in this panel. Keep it conceptual unless sources are attached.

## Screen 2B: VLA / Transformer Readiness

Show whether the model looks like a simple edge model or a transformer/VLA-style workload.

The panel should show:

- matrix-heavy analog opportunity
- attention or attention-like risk
- softmax, layernorm, GeLU, reshape, transpose, and memory movement risks
- digital-required operators
- fallback operators
- analog/digital boundary count
- safe claim level

Example:

```text
Model shape: transformer-like
Analog opportunity: linear projections and feed-forward matrix work
Digital-required work: softmax, layernorm, dynamic attention control
Safe claim: hybrid transformer candidate, not VLA-ready proof
```

This panel should make one point clear: analog MAC efficiency is not the same thing as VLA readiness.

## Screen 2C: Weight Update Readiness

Show whether the product assumes fixed weights or can support adaptation.

The panel should show:

- assumed update pattern
- write latency evidence
- write energy evidence
- endurance evidence
- recalibration after update
- rollback support
- claim boundary

Example:

```text
Update pattern: occasional customer update
Evidence status: no measured on-chip write evidence
Claim boundary: fixed-weight inference only
```

## Screen 2D: Calibration And Drift Gate

Show calibration and drift as reliability gates.

The panel should show:

- temperature range
- voltage range
- calibration provenance
- drift risk
- aging risk
- recalibration status
- fallback behavior if calibration fails
- evidence needed

Example:

```text
Calibration: simulated profile
Drift evidence: missing
Safe claim: analysis only, not safety or production readiness
```

## Screen 2E: Control Boundary

For robotics, mobility, agriculture, defense, and other physical systems, show that inference is not deterministic control.

The panel should show:

- what the inference chip does
- what the real-time controller does
- what the safety monitor does
- expected handoff signal
- latency and jitter evidence
- what not to claim

Example:

```text
Inference role: perception/action support
Control role: external deterministic controller
Missing evidence: bounded jitter and safety handoff behavior
```

## Screen 2F: Compiler Ecosystem Readiness

Show whether developers can actually use the chip from normal model workflows.

The panel should show:

- ONNX status
- PyTorch export status
- JAX/XLA status
- simulator path status
- compiler mapping status
- unsupported operator reporting
- rewrite support
- profiling support
- zero-touch score
- explainable mapping score

Example:

```text
Current path: ONNX
Roadmap path: PyTorch export and JAX/XLA interchange
Adoption risk: manual graph rewrites still required for unsupported operators
```

## Screen 2G: Sensor Boundary

Show where raw physical signals become model-ready tensors.

The panel should show:

- likely sensors
- raw signal type
- preprocessing owner
- AFE status
- event-stream status
- tactile/force status
- timestamp/synchronization status
- energy accounting gap

Example:

```text
Boundary: digital tensor input
Sensor cost: not counted
Missing evidence: preprocessing energy and sensor-to-output latency
```

This is the main landing view after analysis.

Show a verdict card at the top:

```text
Hardware fit: Medium
Analog coverage: 71%
Digital fallback: 8 operators
Main risk: repeated analog/digital crossings around attention
Recommended next step: quantization sensitivity
```

The verdict should be explainable. Each score should have a reason:

- analog coverage: how much compute-heavy work can run on the analog path
- fallback count: how many operators need digital or host execution
- conversion risk: how often data crosses ADC/DAC boundaries
- accuracy risk: how sensitive the model is to low precision or analog error
- deployment risk: unsupported operators or memory pressure

## Screen 3: Layer Placement Table

The layer table is the most useful engineering view.

Columns:

```text
Layer
Operator
Shape
Placement
Reason
Risk
Estimated latency
Estimated energy
```

Example rows:

```text
encoder.matmul.1      MatMul      [1,128,768]    analog core    matrix-heavy, supported      low
encoder.layernorm.1   LayerNorm   [1,128,768]    digital path   not supported in analog      medium
attention.softmax     Softmax     [1,8,128,128]  digital path   nonlinear operator           medium
classifier.dense      MatMul      [1,768,10]     analog core    supported dense layer        low
```

Each row should be selectable. Selecting a row updates the right inspector with:

- why this placement was chosen
- whether the operator is supported
- expected data movement
- ADC/DAC crossings around it
- quantization risk
- suggested rewrite if needed

## Screen 4: Analog/Digital Boundary Map

The boundary map should show where data moves between analog and digital domains.

First version can be a horizontal sequence, not a complex graph:

```text
Input
  -> digital preprocessing
  -> DAC
  -> analog matmul block
  -> ADC
  -> digital normalization
  -> DAC
  -> analog matmul block
  -> ADC
  -> digital output
```

Use color carefully:

- analog path: teal
- digital path: warm gray
- conversion boundary: red/orange
- unsupported/fallback: muted red

The point of this view is to show where energy can be lost. A model with many boundaries may still run, but the user should understand that conversion cost can reduce the benefit.

## Screen 5: Quantization Review

This view should show how much accuracy is at risk when the model is converted into hardware-friendly formats.

The view must first show which modality and task metric are being used. Quantization changes task behavior, and each use case defines bad behavior differently.

Show:

- baseline accuracy
- quantized accuracy
- estimated analog-error accuracy
- worst layers
- sensitive weights or activations
- recommended precision
- modality
- task metric
- primary failure cost
- calibration dataset coverage
- estimated versus measured label

Example:

```text
Baseline accuracy: 94.8%
INT8 accuracy: 94.5%
INT4 accuracy: 91.2%
Analog error estimate: 93.9%
Recommended: INT8 for attention projections, INT4 for feed-forward layers
```

The key design idea: show accuracy as something connected to hardware choices, not as a separate ML metric.

Use-case examples:

```text
Wearable audio
  Metric: false accepts and false rejects
  Risk: noisy input can move small signals across a decision threshold

Smart camera classifier
  Metric: top-1 accuracy and per-class drops
  Risk: first convolution and classifier head may be sensitive

Object detection
  Metric: mAP, recall, confidence threshold movement
  Risk: a small numeric shift can hurt box quality or miss small objects

Robotics perception
  Metric: latency, output jitter, worst-case error
  Risk: average accuracy can look fine while rare outputs become unstable

Industrial anomaly detection
  Metric: anomaly recall and false negatives
  Risk: rare faults can be underrepresented in calibration data

Health wearable
  Metric: sensitivity, specificity, missed events, false alarms
  Risk: physiological signals can be small and user-dependent

Edge LLM
  Metric: perplexity, task quality, token latency
  Risk: attention and output logits can be sensitive to low precision
```

## Screen 6: Calibration View

Calibration should look like a device health and correction view.

Show:

- chip or board ID
- calibration profile version
- temperature range covered
- voltage range covered
- weak memory regions
- correction factors
- last calibration time
- expected accuracy impact

Example:

```text
Calibration status: valid
Board: AS-EDGE-0237
Temperature range: 0C to 70C
Weak rows masked: 12
Expected accuracy impact: -0.3%
```

This helps the customer understand that analog behavior is measured and managed, not guessed.

## Screen 7: Profiling View

Profiling should prove product-level value.

Do not make TOPS/W the main chart. Show:

- energy per inference
- latency per inference
- accuracy after quantization and calibration
- analog compute time
- digital fallback time
- ADC/DAC overhead
- memory movement cost
- idle power
- sustained behavior under heat

Useful chart:

```text
Energy per inference
  analog compute      38%
  ADC/DAC             17%
  memory movement     21%
  digital fallback    16%
  host/runtime         8%
```

This tells the user where the energy is really going.

## Screen 8: Recommendations

The frontend should not only show data. It should tell the user what to try next.

Examples:

```text
Replace unsupported GELU with supported approximation.
Keep LayerNorm on digital path.
Run sensitivity check on attention projection weights.
Reduce analog/digital crossings by fusing matmul blocks.
Try INT4 only on feed-forward layers.
```

Recommendations should be tied to specific layers and specific measured risks.

## Backend API Shape

The frontend needs these core API responses:

```text
POST /models/import
GET  /models/{model_id}/graph
POST /models/{model_id}/analyze-fit
GET  /analyses/{analysis_id}/operator-report
GET  /analyses/{analysis_id}/boundary-map
POST /analyses/{analysis_id}/quantize
GET  /quantization-runs/{run_id}
GET  /devices/{device_id}/calibration
POST /runtime-runs
GET  /runtime-runs/{run_id}/profile
POST /deployment-packages
```

## Data Needed By The Frontend

Operator report:

```json
{
  "layer_id": "encoder.matmul.1",
  "operator": "MatMul",
  "shape": "[1,128,768]",
  "placement": "analog_core",
  "reason": "matrix-heavy supported operator",
  "risk": "low",
  "estimated_latency_ms": 0.42,
  "estimated_energy_uj": 3.1
}
```

Boundary item:

```json
{
  "from": "analog_core",
  "to": "digital_path",
  "boundary": "ADC",
  "reason": "LayerNorm requires digital execution",
  "estimated_energy_uj": 0.8
}
```

Fit summary:

```json
{
  "fit": "medium",
  "analog_coverage_percent": 71,
  "digital_fallback_count": 8,
  "main_risk": "conversion cost around attention blocks",
  "recommended_next_step": "run quantization sensitivity"
}
```

## What To Build First

Build this first:

```text
Model upload/import
Operator extraction
Operator support classification
Fit summary
Layer placement table
Boundary map
Plain-language recommendations
```

Leave calibration, profiling, and deployment packaging for the next phase unless hardware access already exists.

## Clean Product Framing

The frontend should make the hardware honest and usable. It should show where analog helps, where digital fallback is needed, where conversion costs appear, and what the customer should try next. The first useful product is not a dashboard. It is a model-fit workbench.
