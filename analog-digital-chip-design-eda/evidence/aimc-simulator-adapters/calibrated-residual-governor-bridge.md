# Calibrated Residual Governor Bridge

This report connects calibrated simulator evidence to the digital governor.

The object is not the whole transformer. The object is each calibrated fixed-weight subgraph that has a strict simulator payload. Today that means attention-block static projections, one-block transformer-MLP fixed-weight MatMuls, and a deeper three-block transformer-MLP stack. The question is whether each held-out residual is low enough to become a hardware-control request.

## Evidence Rule

A simulator payload must pass two checks before it can request analog service:

1. The payload status must be `wrote_payload`.
2. `accuracy_impact.pass` must be true in the strict payload.

If either check fails, the row is kept as evidence that the tool ran, but it is not allowed to become an analog candidate.

## Governor Rows

| source | tool | accepted | residual | residual q8 | candidate | decision | action | reason |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| attention_block | aihwkit | 0 | 0.609983 | 156 | 0 | 0 | 0 | not_analog_candidate |
| attention_block | crosssim | 1 | 4.17733e-08 | 0 | 1 | 1 | 0 | analog_within_budget |
| transformer_mlp_block | aihwkit | 0 | 0.624664 | 159 | 0 | 0 | 0 | not_analog_candidate |
| transformer_mlp_block | crosssim | 1 | 4.94498e-08 | 0 | 1 | 1 | 0 | analog_within_budget |
| deep_transformer_mlp_stack | aihwkit | 0 | 0.869884 | 222 | 0 | 0 | 0 | not_analog_candidate |
| deep_transformer_mlp_stack | crosssim | 1 | 6.71635e-08 | 0 | 1 | 1 | 0 | analog_within_budget |

## First-Principles Reading

A calibrated simulator result is still not hardware. It is a bounded claim about one software replay. The useful step is to make that bound visible to the controller instead of hiding it in prose.

The bridge turns residual into `residual_q8`, carries a sensitivity field, and asks the same governor used by the other lab traces. CrossSim becomes an analog candidate for the calibrated attention, one-block MLP, and deep MLP-stack fixtures because its held-out residual passes the strict payload check. AIHWKIT does not become a candidate because it ran but exceeded the local threshold.

This is the clean control rule: running a simulator is not enough. Low residual on a held-out calibrated replay can ask for analog service. High residual can only ask for review or fallback.

## Refused Claim

This does not prove silicon calibration, board power, board latency, analog softmax, pretrained model accuracy, physical signoff, or tapeout readiness.
