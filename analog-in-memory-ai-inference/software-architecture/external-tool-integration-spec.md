# External Tool Integration Spec

## Position

The first product version should not require external hardware, compiler tools, or analog circuit tools.

The first version should work locally:

```text
ONNX model
  -> graph analysis
  -> operator fit
  -> analog/digital boundary estimate
  -> estimated quantization sensitivity
  -> simulated runtime profile
  -> plain-language report
```

External tools should be added later behind backend adapters. The frontend should not know whether a result came from a mock estimate, simulator, compiler run, board run, or production device. It should only show the result, provenance, and confidence level.

## Phased Integration

### Phase 1: Local Estimated Analysis

This is the current direction.

Use:

- ONNX graph parsing
- hardware capability rules
- estimated latency and energy models
- modality-aware quantization estimates
- mocked calibration profiles
- simulated runtime profiling

Output:

- model-fit report
- operator placement
- boundary map
- estimated quantization risk
- estimated energy per inference
- simulated completed-inference latency and energy
- simulated bottlenecks and per-layer trace

The simulated runtime profile is deliberately local. It is useful because it forces the product to count host overhead, idle energy, ADC/DAC cost, memory movement, fallback work, and target pass/fail before claiming that the hardware wins.

### Phase 2: Simulator And Tool Integration

Add external software tools only after the local flow is stable.

Likely integrations:

- ONNX Runtime for reference inference
- ONNX Runtime quantization
- PyTorch export flows
- TensorFlow or TFLite import
- TVM, MLIR, IREE, or a custom compiler path
- analog error simulators
- memory-cell variation models

Output:

- measured or simulated accuracy
- real operator-level latency from simulator
- better quantization sensitivity
- compiler-supported placement plans

The backend should replace the local runtime estimator through an adapter, not by changing the frontend contract. The normalized runtime artifact should keep these fields stable:

- provenance
- confidence
- runtime mode
- completed-inference latency
- completed-inference energy
- host overhead
- idle energy
- per-layer trace
- bottlenecks
- recommendations
- target pass/fail

### Phase 3: Board And Silicon Connection

Connect to real hardware after the software path can already explain a model.

Likely integrations:

- board telemetry
- calibration firmware
- runtime traces
- power monitor
- temperature sensors
- JTAG, SWD, or vendor debug path
- device-specific runtime API

Output:

- board-specific calibration profile
- measured latency
- measured energy per inference
- thermal behavior
- runtime failures or fallback traces

### Phase 4: Production Compiler And Runtime

Only after the prototype path proves value, connect the workbench to production tooling.

Likely integrations:

- hardware compiler
- firmware packaging
- runtime deployment package
- versioned calibration artifacts
- production test data
- yield and repeatability reports

Output:

- reproducible deployment package
- traceable model-to-hardware build
- product-level performance report
- readiness evidence for customer integration

## Adapter Architecture

The frontend should call stable backend APIs.

The backend should route work through adapters:

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

Each adapter should return a normalized artifact. The UI should render the normalized artifact instead of rendering tool-specific output.

Current implementation:

- `GET /adapters` returns the adapter registry.
- `GET /adapters/{adapter_id}/probe` runs a lightweight connection probe and returns the normalized evidence contract for that adapter.
- `POST /adapters/{adapter_id}/run?model_id=...` runs a local adapter implementation when one exists.
- `POST /deployment-packages/{package_id}/local-evidence` runs all local evidence adapters for a saved package and imports the normalized artifacts. It refreshes previous local-generated artifacts and skips sources that already have non-local evidence unless forced.
- `GET /deployment-packages/{package_id}/connection-playbook` returns the real-tool wiring checklist for quantization, compiler mapping, analog simulation, dataset accuracy, board runtime, and power or thermal measurement.
- The registry marks local estimators as available.
- It checks Python dependencies for ONNX, ONNX Runtime, TVM, and IREE.
- It checks `ANALOG_AI_BOARD_API_URL` for board runtime configuration.
- It checks `ANALOG_AI_POWER_METER_URL` for power and thermal measurement configuration.

This does not connect hardware yet. It makes the connection state visible so the product does not confuse local estimates with measured external evidence.

The probe endpoint is the first executable adapter surface. For local adapters it checks Python package availability. For board and power adapters it checks the configured environment variables and tries a short `/health` call against the configured service URL. For compiler, analog simulation, board runtime, power, and accuracy paths it also returns the evidence artifact name and minimum fields that must be imported before the workbench treats the result as claim support.

The first runnable adapters are `quantization.onnxruntime`, `compiler.tvm-mlir-iree`, `analog.error-simulator`, `accuracy.local-task-check`, `board.runtime`, and `metrics.power-thermal`. When ONNX Runtime is installed, the quantization adapter creates a dynamic INT8 ONNX model under backend `.data/adapter-runs/` and returns file-size and graph summaries. When ONNX Runtime is not installed, it returns a blocked adapter-run result with the missing dependency and next step. Either result is still not accuracy evidence by itself. A task dataset must produce `task-accuracy-report.json` before accuracy claims become supported.

The compiler adapter currently uses the local analyzer placement rules to generate `compiler-placement.json`. That is useful because it exercises the same evidence import path that a real compiler will use later. It should be described as local placement evidence, not as proof from TVM, IREE, MLIR, or a production compiler. A real compiler can replace this runner later without changing the frontend contract.

The analog error adapter currently uses the selected calibration profile and model placement summary to generate `analog-error-simulation.json`. It estimates temperature range, voltage range, ADC/DAC settings, gain and offset correction, and a low-confidence accuracy-impact proxy. This is useful for testing the claim gates, but it is not a substitute for circuit simulation, silicon characterization, or board-measured numeric error. Accuracy still needs a matching `task-accuracy-report.json`.

The task accuracy adapter can now generate `task-accuracy-report.json` from a local dataset file when `dataset_path` is provided. The dataset file supplies expected labels, baseline predictions, candidate predictions, metric name, and tolerance. When no dataset is provided, the adapter still falls back to the synthetic quantization-plus-analog-error estimate so the evidence flow can be tested. The dataset-backed path is a better first proof shape, but a real product flow should still replace the sample predictions with outputs from the actual mapped candidate model and the target task dataset.

The board runtime and power/thermal adapters currently generate `board-runtime-trace.json` and `power-thermal-report.json` from the local runtime simulator. They exercise the latency and energy evidence paths, but claim readiness marks these local simulated payloads as `needs review` rather than measured support. Real board traces and synchronized power/thermal measurements should replace them for measured latency and energy claims.

Generated evaluation archives include `adapter-registry.json` and `measurement-evidence.json`. Evidence gates and review reports also summarize adapter state, because the safe claim depends on whether compiler, simulator, board runtime, power measurement, and task-accuracy sources are connected or still only planned.

Generated evaluation archives also include `connection-playbook.json`. This is the practical handoff for replacing local estimates with real tools. For each connection it states what to configure, which normalized artifact must be imported, what that artifact can prove, what it cannot prove, and the next action.

The measurement evidence artifact is the contract between external tools and product claims. It lists the normalized files that must exist before a claim can change from estimated to measured:

- `compiler-placement.json`
- `analog-error-simulation.json`
- `board-runtime-trace.json`
- `power-thermal-report.json`
- `task-accuracy-report.json`

A configured adapter is not enough. The backend must receive a normalized artifact with provenance, target settings, source version, metrics, confidence, and raw-output references before the frontend treats it as evidence.

Configured-service failure is also part of the contract. If an external service cannot be reached, returns an HTTP error, returns non-JSON, or returns JSON without the required normalized evidence payload, the adapter run must stop as `blocked`. It must not fall back to the local estimator, because that would make a broken external path look successful. The run should save `external-service-request.json`, save `external-service-response.json` when a response exists, and save `external-service-failure.json` with the URL, source ID, artifact name, error, and next step. That failure artifact is not claim evidence, but it is important audit evidence for integration work.

The first ingestion paths are `POST /evidence/import` and `POST /evidence/import-batch`. They accept normalized artifacts for specific `source_id` values and attach them to a package or run. The measurement contract can then report each source as an imported artifact while keeping the other sources blocked or estimated.

Claim readiness is recalculated from imported evidence. A compiler artifact can support placement discussion, but it cannot support latency, energy, or accuracy claims. A board runtime artifact can support latency, but measured energy still needs power or thermal evidence. Local simulated board and power artifacts move latency and energy claims to `needs review`, not `supported`. Accuracy needs both analog-error evidence and task-accuracy evidence, and the task-accuracy payload must pass its own tolerance check. If `task-accuracy-report.json` says `pass: false`, the accuracy claim moves to `needs review`, not `supported`. Production readiness remains blocked even when lab claims are supported.

## Adapter Types

### Model Import Adapter

Purpose:

Convert a customer model into the internal graph format.

Possible tools:

- ONNX
- PyTorch export
- TensorFlow
- TFLite

Normalized output:

- model graph
- operator list
- shapes
- parameter count
- weights
- unsupported structures

### Quantization Adapter

Purpose:

Convert the model to hardware-supported number formats and estimate or measure task impact.

Possible tools:

- ONNX Runtime quantization
- PyTorch quantization
- custom analog-aware quantizer
- Brevitas or QONNX-style flows

Normalized output:

- baseline metric
- quantized metric
- per-layer sensitivity
- recommended precision
- protected layers or weights
- result provenance

### Compiler Adapter

Purpose:

Map model blocks onto analog and digital hardware paths.

Possible tools:

- MLIR
- TVM
- IREE
- custom hardware compiler

Normalized output:

- analog placement
- digital placement
- fallback placement
- tiling plan
- memory plan
- ADC/DAC boundary plan
- unsupported operator list

### Analog Simulation Adapter

Purpose:

Estimate analog behavior before silicon or board access.

Possible tools:

- SPICE
- Spectre
- HSPICE
- ngspice
- custom error model
- memory-cell variation model
- ADC/DAC model

Normalized output:

- error model
- calibration assumptions
- conversion cost
- variation sensitivity
- expected accuracy impact
- confidence level

### Digital Hardware Adapter

Purpose:

Use digital implementation data when available.

Possible tools:

- Verilog or SystemVerilog simulation
- Verilator
- cocotb
- synthesis reports
- timing reports
- power reports

Normalized output:

- supported digital operators
- digital fallback cost
- timing estimate
- power estimate
- resource usage

### Board Runtime Adapter

Purpose:

Run prepared models on a real board or chip.

Possible tools:

- board runtime API
- calibration firmware
- telemetry collector
- power meter
- temperature monitor
- debug interface

Normalized output:

- measured latency
- measured energy
- output trace
- temperature trace
- voltage trace
- calibration profile
- runtime warnings

## Provenance And Confidence

Every result must say where it came from.

Allowed provenance labels:

```text
mock
estimated
simulated
compiler_report
prototype_board
production_board
customer_device
```

Allowed confidence labels:

```text
low
medium
high
measured
```

The frontend must show these labels. A result from a mock profile should not look the same as a result from measured silicon.

## API Rule

Do not expose tool-specific details directly to the frontend.

Good API shape:

```json
{
  "result_type": "quantization_report",
  "provenance": "simulated",
  "confidence": "medium",
  "metric": "false_reject_rate",
  "summary": "...",
  "layer_recommendations": []
}
```

Avoid frontend-specific coupling to a tool:

```text
Do not make the UI parse raw SPICE output.
Do not make the UI parse compiler logs.
Do not make the UI parse board telemetry streams directly.
```

The backend should translate raw tool output into product-level artifacts.

## Acceptance Criteria

- The local prototype works without external hardware tools.
- Every result has provenance and confidence.
- External tools are integrated through adapters.
- The frontend contract stays stable as tools are added.
- Raw compiler, simulator, circuit, and board outputs are stored for audit but normalized before display.
- Failed configured-service runs are blocked and archived with request, response when present, and failure details.
- The report can distinguish estimated, simulated, prototype-board, and production-board evidence.

## Clean Design Principle

Build the workflow locally first. Add external compilers, simulators, analog tools, digital tools, and hardware connections behind backend adapters. The frontend should show what the result means, how confident it is, and what evidence produced it.
