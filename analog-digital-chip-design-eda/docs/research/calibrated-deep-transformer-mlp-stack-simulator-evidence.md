# Calibrated Deep Transformer MLP Stack Simulator Evidence

This page explains the larger source-matched simulator replay.

The earlier calibrated MLP fixture had one block and four fixed-weight MatMuls. This fixture has three repeated MLP-style blocks and twelve fixed-weight MatMuls. That matters because analog error is not only a property of one multiply. In a deeper chain, the output of one block becomes the input to the next block, so small differences can be carried forward, clipped by ReLU, multiplied by a gate, added through a residual path, and then multiplied again.

## Object

The object is `deep-transformer-mlp-stack.onnx`.

The calibrated analog candidates are twelve fixed-weight MatMul nodes:

- `block0.gate.matmul`
- `block0.up.matmul`
- `block0.down.matmul`
- `block0.out.matmul`
- `block1.gate.matmul`
- `block1.up.matmul`
- `block1.down.matmul`
- `block1.out.matmul`
- `block2.gate.matmul`
- `block2.up.matmul`
- `block2.down.matmul`
- `block2.out.matmul`

The digital-only operations remain bias adds, ReLUs, elementwise gate mixing, and residual adds.

## Constraint

A deeper replay is still not a foundation model.

The useful claim is narrower: the system can run a repeated fixed-weight MatMul stack through simulator APIs, learn a correction from separate inputs, test on a held-out input, and decide which tool is allowed to support an analog claim. It still does not prove token accuracy, pretrained model behavior, silicon calibration, board runtime, measured power, analog activation, analog residual addition, or physical macro signoff.

## Design Move

Run:

```bash
/home/mehtama1/eda-tools/aimc-simulators-venv/bin/python scripts/run_calibrated_deep_transformer_mlp_stack_aimc_simulator_payloads.py
```

The script reads:

- `/home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/samples/deep-transformer-mlp-stack.onnx`

It writes:

- `evidence/aimc-simulator-adapters/aihwkit-calibrated-deep-transformer-mlp-stack-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-calibrated-deep-transformer-mlp-stack-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/calibrated-deep-transformer-mlp-stack-simulator-payload-run-summary.json`

## Evidence

The current local run uses seven calibration inputs and one held-out input.

For each MatMul, the script records the digital input vector that reached that MatMul during normal graph execution. It asks the simulator for that MatMul output, fits a per-output affine correction from calibration cases, and then tests the corrected simulator output on the held-out case.

CrossSim writes a passing payload for the twelve-MatMul stack. AIHWKIT writes a payload too, but its residual remains above the positive-claim threshold, so it is kept as run evidence and rejected as positive claim evidence.

The important point is the control rule. The analog claim does not come from the words "AIHWKIT" or "CrossSim." It comes from the measured residual inside the payload. The same fixture accepts one tool and refuses the other.

## Allowed Claim

The system can say:

CrossSim now runs a calibrated simulator payload for a three-block transformer-MLP-style ONNX fixture with twelve fixed-weight MatMul candidates. AIHWKIT runs the same deeper fixture but is not accepted as positive claim evidence because its held-out residual remains above the threshold.

## Refused Claim

The system cannot say:

- a pretrained foundation model has been proven
- token accuracy has been measured
- analog activations, gate mixing, or residual adds have been proven
- calibration has been proven on silicon
- the correction is stable across voltage, temperature, drift, or aging
- board latency or power has been measured
- this is a physical macro placement
- the design is ready for signoff or tapeout

## Next Handoff

The next proof is to feed this deeper calibrated MLP-stack result into the generalized residual governor as another source-matched fixed-weight MatMul source. That would let placement prefer the deepest available matching source for dense MLP-like rows, while still refusing to inherit that evidence for bias, activation, residual, softmax, or dynamic attention work.
