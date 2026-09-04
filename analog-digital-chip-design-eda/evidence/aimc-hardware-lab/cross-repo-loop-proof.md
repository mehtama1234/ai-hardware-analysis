# Cross-Repo AIMC Loop Proof

This report records the proof that the restored workbench and the newer hardware lab are connected as one loop.

## What Ran

```text
backend health
  -> backend hardware placement
  -> hardware-lab placement import
  -> governor request generation
  -> generated Verilog governor cases
  -> RTL trace check
  -> AIHWKIT/CrossSim adapter availability check
  -> optional AIHWKIT/CrossSim payload run path
  -> tensor-shaped AIHWKIT/CrossSim payload run path
  -> trained-weight AIHWKIT/CrossSim payload run path
  -> projection-stack AIHWKIT/CrossSim payload run path
  -> transformer-MLP-block AIHWKIT/CrossSim payload run path
  -> calibrated transformer-MLP-block AIHWKIT/CrossSim payload run path
  -> calibrated deep transformer-MLP-stack AIHWKIT/CrossSim payload run path
  -> attention-block AIHWKIT/CrossSim payload run path
  -> calibrated attention-block AIHWKIT/CrossSim payload run path
  -> calibrated residual governor bridge
  -> residual-aware placement decisions
  -> hardware-lab evidence export
  -> backend hardware-lab evidence import
  -> package claim-readiness refresh
```

## Result

- status: PASS
- package: pkg-e931662a01293df2
- backend operators: 5
- backend analog candidates: 2
- governor rows: 10
- backend governor rows: 5
- RTL: pass
- exported evidence records: 6
- backend import accepted: 6
- strict simulator/tool evidence imported: True
- AIHWKIT adapter: available
- CrossSim adapter: available
- optional simulator payloads: {"aihwkit": "wrote_payload", "crosssim": "wrote_payload"}
- tensor-shaped simulator payloads: {"aihwkit": "wrote_payload", "crosssim": "wrote_payload"}
- trained-weight simulator payloads: {"aihwkit": "wrote_payload_threshold_fail", "crosssim": "wrote_payload"}
- projection-stack simulator payloads: {"aihwkit": "wrote_payload_threshold_fail", "crosssim": "wrote_payload"}
- transformer-MLP-block simulator payloads: {"aihwkit": "wrote_payload_threshold_fail", "crosssim": "wrote_payload"}
- calibrated transformer-MLP-block simulator payloads: {"aihwkit": "wrote_payload_threshold_fail", "crosssim": "wrote_payload"}
- calibrated deep transformer-MLP-stack simulator payloads: {"aihwkit": "wrote_payload_threshold_fail", "crosssim": "wrote_payload"}
- attention-block simulator payloads: {"aihwkit": "wrote_payload_threshold_fail", "crosssim": "wrote_payload"}
- calibrated attention-block simulator payloads: {"aihwkit": "wrote_payload_threshold_fail", "crosssim": "wrote_payload"}
- calibrated residual governor rows: 6
- calibrated residual analog decisions: 3
- residual-aware placement allowed rows: 2

## Claim Status

- supported lab claims: 3
- needs-review lab claims: 2
- blocked lab claims: 0
- production claim: blocked
- overall: claim evidence needs review

## What This Proves

The model graph in the restored backend can produce a hardware-placement artifact. The hardware lab can import that artifact, convert it into governor-sized rows, generate Verilog cases, pass the RTL checker, check optional AIHWKIT/CrossSim availability, run small optional simulator fixtures, run tensor-shaped simulator payloads for the backend analog MatMul candidates, run trained-weight simulator payloads from the uploaded ONNX model, run a larger projection-stack ONNX replay, run a transformer-MLP-shaped ONNX replay with nonlinear and residual operations kept digital, run a held-out calibrated MLP replay, run a deeper held-out calibrated MLP-stack replay, run an attention-shaped ONNX replay with static projections separated from dynamic attention operations, run a held-out calibrated attention replay, convert calibrated residuals into governor decisions, filter structural placement through those residual-aware decisions, export normalized evidence, re-import that evidence into the backend package, and keep the deployment archive aligned with the API for residual-aware placement and C2/C3 claim-readiness boundaries.

## What This Does Not Prove

This does not prove measured board latency, measured energy, calibrated silicon behavior, pretrained foundation-model AIHWKIT/CrossSim agreement, analog macro layout, package reliability, or tapeout readiness. The backend correctly keeps latency and energy in needs-review status and keeps production readiness blocked. Measured energy needs measured runtime and measured power tied to the same runtime trace ID, package, workload, board, start time, and end time.
