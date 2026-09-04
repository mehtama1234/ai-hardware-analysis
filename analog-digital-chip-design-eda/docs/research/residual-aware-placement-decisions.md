# Residual-Aware Placement Decisions

This page explains the next step after the calibrated residual governor bridge.

The earlier placement proof answered one question: which backend operators are shaped like analog work? This page answers the next question: after calibrated simulator evidence is available, which of those operators are still allowed to use analog service?

## Object

The object is the backend hardware placement artifact joined with generalized calibrated simulator evidence.

The placement artifact has five backend operators:

- `dense1.matmul`
- `dense1.bias`
- `dense1.relu`
- `dense2.matmul`
- `dense2.bias`

Only the two MatMul rows are structural analog candidates.

## Constraint

Structural fit is not evidence of correctness.

A MatMul can match the shape of an analog crossbar and still be refused if the calibrated residual is too high. A bias add, activation, softmax, or dynamic attention operation should not inherit a MatMul simulator result just because it appears nearby in the model graph.

## Design Move

Run:

```bash
python3 scripts/run_residual_aware_placement_decisions.py
```

The script reads:

- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/backend-hardware-placement.json`
- `evidence/aimc-simulator-adapters/calibrated-residual-governor-bridge.json`

It writes:

- `evidence/aimc-simulator-adapters/residual-aware-placement-decisions.json`
- `evidence/aimc-simulator-adapters/residual-aware-placement-decisions.md`
- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/residual-aware-placement-decisions.csv`

## Evidence

The current accepted calibrated residuals come from CrossSim for the attention, one-block transformer-MLP, and deep transformer-MLP stack fixture sources. The residual-aware placement file records which accepted calibrated source was used for the backend MatMul rows.

The selection rule is a fixed-weight MatMul family match. The backend rows are named `dense1.matmul` and `dense2.matmul`, so the chosen source is the calibrated deep transformer-MLP stack, whose object is twelve repeated fixed-weight MatMuls. The one-block transformer-MLP fixture remains the next fallback. The attention fixture also passes, but it is only a fallback for attention-like projection rows. It is not the first source for this dense MLP-shaped backend placement.

The three non-MatMul rows remain digital. They are not refused because CrossSim failed. They are refused because their operation is not the fixed-weight multiply object that the calibrated simulator evidence covers.

## Allowed Claim

The system can say:

Backend placement rows now pass through a residual-aware evidence filter. Structural MatMul candidates must be backed by accepted calibrated simulator evidence, including the accepted source object and source matching policy, before they remain analog-allowed.

## Refused Claim

The system cannot say:

- all backend operators can run on analog
- analog softmax has been proven
- analog dynamic attention has been proven
- silicon behavior has been calibrated
- board power or latency has been measured
- the placement is a physical macro placement
- the design is ready for signoff or tapeout

## Next Handoff

That backend handoff is now implemented. The old workbench exposes the residual-aware view at:

```text
http://127.0.0.1:8025/deployment-packages/pkg-e931662a01293df2/residual-aware-placement
```

The saved deployment archive also carries `residual-aware-placement.json`, and the 50-gate bridge checks that the archived JSON matches the endpoint summary and source policy.

The next proof is not another label in the UI. The next proof is stronger evidence under the same source-matched decision rule: measured board latency, synchronized power, physical analog macro evidence, or a calibrated simulator result for a larger real model that keeps the residual inside the allowed boundary.
