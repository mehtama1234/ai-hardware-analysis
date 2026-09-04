# Transformer MLP Block Simulator Evidence

This page explains the larger fixed-weight simulator replay.

The earlier projection-stack proof used four MatMuls in a simple chain. The attention-block proof added dynamic attention and kept softmax digital. This proof adds a transformer-MLP-shaped block: two input projections, a digital elementwise mix, a down projection, a residual add, and an output projection.

## Object

The object is `transformer-mlp-block.onnx`.

The analog candidates are only the fixed-weight MatMuls:

- `mlp.gate.matmul`
- `mlp.up.matmul`
- `mlp.down.matmul`
- `mlp.out.matmul`

The digital-only operations are bias adds, ReLUs, the elementwise multiply, and the residual add.

## Constraint

A transformer MLP is not just one matrix multiply.

The gate and up projections create two different hidden states. The elementwise multiply combines them. The down projection returns the hidden state to the model width. The residual add mixes the block output with the original input. If analog error changes one projection, the error can change what later digital operations receive.

That is why the proof cannot stop at "the MatMul ran." The useful question is whether replacing the fixed-weight MatMuls with simulator outputs keeps the final block output inside the residual boundary.

## Design Move

Run:

```bash
/home/mehtama1/eda-tools/aimc-simulators-venv/bin/python scripts/run_transformer_mlp_block_aimc_simulator_payloads.py
```

The script reads:

- `/home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/samples/transformer-mlp-block.onnx`

It writes:

- `evidence/aimc-simulator-adapters/aihwkit-transformer-mlp-block-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-transformer-mlp-block-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/transformer-mlp-block-simulator-payload-run-summary.json`

## Evidence

The current local run covers four fixed-weight MatMul candidates.

CrossSim writes a payload that passes the positive simulator-evidence threshold. AIHWKIT writes a payload too, but its residual is above the local threshold, so it is not accepted as positive claim evidence.

This is the same pattern as the projection and attention proofs. The system records both tools, but only the result inside the error boundary can support an analog placement or governor decision.

## Allowed Claim

The system can say:

CrossSim now runs a strict simulator payload for a transformer-MLP-shaped ONNX fixture with four fixed-weight MatMul candidates, while the nonlinear and residual operations remain digital. AIHWKIT also runs the same fixture, but the current payload is rejected for a positive simulator claim because its residual is above the local threshold.

## Refused Claim

The system cannot say:

- a pretrained foundation model has been proven
- token accuracy has been measured
- the residual path is safe on silicon
- the elementwise mix or residual add runs in analog
- board latency or power has been measured
- this is a physical macro placement
- the design is ready for signoff or tapeout

## Next Handoff

The next proof is to calibrate this MLP-block replay on separate inputs, then feed only accepted residuals into the same governor and residual-aware placement path. That would move the proof from "larger uncalibrated fixture" to "larger held-out calibrated fixture" without changing the claim boundary.
