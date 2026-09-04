# Trained-Weight Simulator Evidence

This page explains the strongest simulator proof currently available in the local workbench.

The earlier tensor-shaped replay used the right operator shapes but generated fixture weights. This replay uses the actual initializer weights from the uploaded `tiny-mlp.onnx` model.

## Object

The object is the analog part of the current backend package model:

- source model: `ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/samples/tiny-mlp.onnx`
- backend package: `pkg-e931662a01293df2`
- analog operators: `dense1.matmul` and `dense2.matmul`
- digital support operators: `dense1.bias`, `dense1.relu`, and `dense2.bias`

The ONNX initializers are:

- `w1`: 4 inputs by 3 outputs
- `b1`: 3 outputs
- `w2`: 3 inputs by 2 outputs
- `b2`: 2 outputs

The replay runs the MatMul weights through AIHWKIT and CrossSim. Bias and ReLU stay in ordinary digital arithmetic because the backend placement marks them as digital support operators.

The current result is intentionally split:

- CrossSim stays inside the positive-claim residual threshold.
- AIHWKIT runs the same weights, but its current output residual is above the positive-claim threshold, so the guarded importer rejects it as supporting evidence.

## Constraint

This is a real-weight simulator replay, not a hardware measurement.

It proves that the uploaded tiny MLP weights can pass through the analog simulator adapter path for the backend-selected analog operators. It does not prove a foundation model, token accuracy, calibrated device drift, board latency, board power, analog macro layout, or signoff.

## Design Move

Run:

```bash
python3 scripts/run_trained_weight_aimc_simulator_payloads.py
```

The script uses two Python environments for a narrow reason:

- the old backend `.venv` reads ONNX initializers
- the AIMC simulator venv runs AIHWKIT and CrossSim

The script extracts `w1`, `b1`, `w2`, and `b2`; computes a digital reference; runs only the analog MatMul operators through AIHWKIT and CrossSim; applies bias and ReLU digitally; and writes strict payloads.

The output files are:

- `evidence/aimc-simulator-adapters/aihwkit-trained-weight-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-trained-weight-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/trained-weight-simulator-payload-run-summary.json`

Each positive-claim payload must pass:

```bash
python3 scripts/import_analog_simulator_payload.py <payload.json>
```

For the current AIHWKIT trained-weight payload, the expected guard behavior is rejection:

```bash
python3 scripts/import_analog_simulator_payload.py --expect-reject evidence/aimc-simulator-adapters/aihwkit-trained-weight-analog-error-simulation.json
```

## Evidence

This proof is stronger than shape-only replay because the numbers in the MatMul arrays are the model weights, not generated placeholders.

The evidence chain is:

- ONNX model stores the trained weights
- backend placement chooses the MatMul operators for analog execution
- simulator script maps those weights into AIHWKIT and CrossSim
- digital reference computes the same graph with normal arithmetic
- guarded importer checks the payload schema and backend tool-readiness rules

The residual is the relative L2 difference between the digital ONNX-weight path and the simulator path.

## Allowed Claim

The system can say:

CrossSim now runs a strict simulator payload using the uploaded tiny MLP ONNX weights for the backend-selected analog MatMul operators, and that payload passes the guarded evidence importer. AIHWKIT also runs the same trained-weight replay, but the current payload is rejected for a positive simulator claim because its residual is above the local threshold.

## Refused Claim

The system cannot say:

- a foundation model has been simulated
- token accuracy has been measured
- device drift has been calibrated
- board latency has been measured
- board power has been measured
- analog macro layout has been verified
- the design is ready for tapeout

## Next Handoff

The next proof is larger-model replay.

That means importing a more realistic transformer or projection-heavy ONNX model, preserving its real weights, identifying which static-weight MatMul operators are good analog candidates, and running those exact weights through AIHWKIT and CrossSim with the same guarded payload path.
