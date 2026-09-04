# Calibrated Attention-Block Simulator Evidence

This page explains the calibrated attention-shaped replay.

The raw attention-block replay asks whether static Q, K, V, and output projection weights can run through AIHWKIT and CrossSim while dynamic attention stays digital. This page adds one correction rule: a per-output affine calibration learned from separate input cases.

## Object

The object is still `attention-block.onnx`.

The analog-covered operators are:

- `attn.q.matmul`
- `attn.k.matmul`
- `attn.v.matmul`
- `attn.out.matmul`

The digital-only attention operators are:

- `attn.scores.matmul`
- `attn.scale`
- `attn.softmax`
- `attn.value.matmul`

## Constraint

Calibration is not magic.

The script learns one gain and one offset per output channel from calibration inputs. It then tests a different held-out input. That can correct stable scale and offset error. It cannot prove drift over time, temperature behavior, voltage sensitivity, real device programming error, board latency, board power, or pretrained model quality.

## Design Move

Run:

```bash
python3 scripts/run_calibrated_attention_block_aimc_simulator_payloads.py
```

The script:

- extracts the real ONNX initializer weights
- runs four separate calibration input cases
- fits per-output affine correction for each static projection
- runs the held-out attention input
- keeps dynamic score, softmax, and value mixing in digital arithmetic
- writes strict simulator payloads

The output files are:

- `evidence/aimc-simulator-adapters/aihwkit-calibrated-attention-block-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-calibrated-attention-block-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/calibrated-attention-block-simulator-payload-run-summary.json`

## Evidence

The current result is split:

- CrossSim passes the guarded positive-evidence check after calibration.
- AIHWKIT still exceeds the local residual threshold and is rejected for a positive claim.

That is useful because it separates three things:

- the simulator can run
- the correction rule can help one simulator
- the guard still refuses a weak numerical result

## Allowed Claim

The system can say:

CrossSim now runs a calibrated attention-shaped replay where static projection weights use held-out affine correction and dynamic attention operations remain digital. AIHWKIT also runs the calibrated replay, but the current payload is rejected for a positive claim because its residual is above the local threshold.

## Refused Claim

The system cannot say:

- calibration proves silicon behavior
- analog attention has been proven
- softmax has been moved to analog
- value mixing has been moved to analog
- token accuracy has been measured
- a pretrained foundation model has been simulated
- board latency or board power has been measured
- the design is ready for tapeout

## Next Handoff

The next proof is a better mapping decision, not broader wording.

Use the replay results to decide which projection paths are safe enough for analog under the current simulator settings. Then feed that decision back into the governor so analog is selected only when the calibrated residual is inside the model's error budget.
