# Calibrated Transformer MLP Block Simulator Evidence

This page explains the held-out calibration proof for the transformer-MLP-shaped fixture.

The uncalibrated MLP-block replay asks whether the four fixed-weight MatMuls can run through AIHWKIT and CrossSim while the nonlinear and residual operations stay digital. This page adds one stricter step: learn a per-output affine correction on separate input vectors, then test the corrected simulator output on a held-out input.

## Object

The object is still `transformer-mlp-block.onnx`.

The calibrated analog candidates are:

- `mlp.gate.matmul`
- `mlp.up.matmul`
- `mlp.down.matmul`
- `mlp.out.matmul`

The digital-only operations remain bias adds, ReLUs, the elementwise multiply, and the residual add.

## Constraint

Calibration is not permission to claim hardware.

Calibration only says: under this software simulator, for this fixed model fixture, a simple correction learned from separate inputs reduced the held-out residual enough to pass or failed to do so. It does not say the same correction will hold across voltage, temperature, drift, aging, devices, boards, or real token distributions.

## Design Move

Run:

```bash
/home/mehtama1/eda-tools/aimc-simulators-venv/bin/python scripts/run_calibrated_transformer_mlp_block_aimc_simulator_payloads.py
```

The script reads:

- `/home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/samples/transformer-mlp-block.onnx`

It writes:

- `evidence/aimc-simulator-adapters/aihwkit-calibrated-transformer-mlp-block-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-calibrated-transformer-mlp-block-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/calibrated-transformer-mlp-block-simulator-payload-run-summary.json`

## Evidence

The current local run fits per-output affine correction on five calibration vectors and tests on one held-out vector.

CrossSim passes the guarded positive-evidence threshold after calibration. AIHWKIT also runs the calibrated replay, but its held-out residual remains above the local threshold, so it is rejected for a positive simulator claim.

The important result is not that calibration exists. The important result is that the same rule accepts one tool and refuses the other based on held-out residual, while keeping nonlinear and residual operations digital.

## Allowed Claim

The system can say:

CrossSim now runs a calibrated simulator payload for a transformer-MLP-shaped ONNX fixture with four fixed-weight MatMul candidates. AIHWKIT runs the same calibrated fixture but is not accepted as positive claim evidence because its held-out residual remains above the threshold.

## Refused Claim

The system cannot say:

- a pretrained foundation model has been proven
- token accuracy has been measured
- calibration has been proven on silicon
- the elementwise mix or residual add runs in analog
- the correction is stable across voltage, temperature, drift, or aging
- board latency or power has been measured
- this is a physical macro placement
- the design is ready for signoff or tapeout

## Next Handoff

The next proof is to feed this calibrated MLP-block result into a generalized residual governor, alongside the calibrated attention result. The governor should not care whether the source is attention or MLP. It should care about the same fields: tool, target object, held-out residual, sensitivity, and allowed claim boundary.
