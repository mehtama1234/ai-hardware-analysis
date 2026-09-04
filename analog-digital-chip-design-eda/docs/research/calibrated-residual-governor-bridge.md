# Calibrated Residual Governor Bridge

This page explains the next bridge after AIHWKIT/CrossSim installation.

The simulator proof says whether a tool can run a calibrated replay. The governor proof asks a different question: can the result be turned into a hardware decision without pretending it is silicon?

## Object

The object is each calibrated fixed-weight subgraph that has a strict simulator payload:

- `attention-block.onnx` static projections
- `transformer-mlp-block.onnx` fixed-weight MatMuls
- `deep-transformer-mlp-stack.onnx` twelve fixed-weight MatMuls across three repeated MLP-style blocks

The replay covers:

- `attn.q.matmul`
- `attn.k.matmul`
- `attn.v.matmul`
- `attn.out.matmul`

It does not cover the dynamic attention score matrix, softmax, or value mixing as analog operations.

For the MLP fixtures, it covers only fixed-weight MatMuls. Bias adds, ReLUs, elementwise gate mixing, and residual adds stay digital.

## Constraint

A simulator run is not enough.

The bridge accepts a payload only when the payload status is `wrote_payload` and the strict payload says `accuracy_impact.pass` is true. A payload that ran but exceeded the local residual threshold is recorded, but it cannot request analog service.

## Design Move

Run:

```bash
python3 scripts/run_calibrated_residual_governor_bridge.py
```

The script reads:

- `evidence/aimc-simulator-adapters/calibrated-attention-block-simulator-payload-run-summary.json`
- `evidence/aimc-simulator-adapters/calibrated-transformer-mlp-block-simulator-payload-run-summary.json`
- `evidence/aimc-simulator-adapters/calibrated-deep-transformer-mlp-stack-simulator-payload-run-summary.json`
- `evidence/aimc-simulator-adapters/aihwkit-calibrated-attention-block-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-calibrated-attention-block-analog-error-simulation.json`

It writes:

- `evidence/aimc-simulator-adapters/calibrated-residual-governor-bridge.json`
- `evidence/aimc-simulator-adapters/calibrated-residual-governor-bridge.md`
- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/calibrated-residual-governor-requests.csv`

## Evidence

CrossSim becomes an analog candidate for the governor because it passes the calibrated attention-block payload, the calibrated transformer-MLP-block payload, and the calibrated deep transformer-MLP-stack payload.

AIHWKIT does not become a candidate. It runs the same calibrated bridge, but its payloads are not accepted as positive evidence because their residuals are above the local threshold. The governor rows therefore keep it out of analog service.

## Allowed Claim

The system can say:

Calibrated simulator residuals now feed a governor decision path. CrossSim can request analog service for the calibrated static attention projections, calibrated one-block transformer-MLP MatMuls, and calibrated deep transformer-MLP-stack MatMuls in these fixtures. AIHWKIT cannot request analog service for the same fixtures because the measured residual is too high.

## Refused Claim

The system cannot say:

- the attention block has been proven on silicon
- analog softmax has been implemented
- dynamic attention has been mapped to analog arrays
- board latency or power has been measured
- pretrained foundation-model accuracy has been preserved
- the design is ready for signoff or tapeout

## Next Handoff

The placement proof now chooses from the generalized bridge by source fit. The backend dense MatMul rows use the calibrated deep transformer-MLP-stack source, while the one-block transformer-MLP source and attention projection evidence remain fallbacks for their matching rows. The next proof is stronger evidence under that same rule: measured board runtime, synchronized power, physical macro evidence, or a larger calibrated model replay that stays inside the residual boundary.
