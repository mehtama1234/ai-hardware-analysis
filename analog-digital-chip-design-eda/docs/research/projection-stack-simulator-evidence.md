# Projection-Stack Simulator Evidence

This page explains the larger trained-weight simulator replay.

The tiny MLP proof showed that real ONNX weights can be extracted and run through AIHWKIT and CrossSim. This page raises the object size and shape: four learned projection matrices with digital bias and ReLU support between them.

## Object

The object is `projection-stack.onnx`.

It is not a pretrained language model. It is a local ONNX fixture built to look like the repeated projection work that makes analog in-memory compute interesting:

- `proj.q.matmul`: 8 inputs by 16 outputs
- `proj.k.matmul`: 16 inputs by 16 outputs
- `proj.v.matmul`: 16 inputs by 12 outputs
- `proj.out.matmul`: 12 inputs by 8 outputs

Between those MatMul operators, the graph keeps bias and ReLU in digital arithmetic. That matches the system idea: analog arrays handle repeated static-weight multiply work, while digital logic handles support operations and boundary decisions.

## Constraint

This proof is larger than the tiny MLP proof, but it is still a fixture.

It proves that real ONNX initializer weights for a multi-projection graph can run through the simulator adapter path. It does not prove pretrained foundation-model behavior, attention, softmax, layer normalization, token accuracy, silicon behavior, board latency, board power, or layout.

## Design Move

Generate the ONNX fixture with:

```bash
/home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/backend/.venv/bin/python /home/mehtama1/git-repo/ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/samples/make-projection-stack-onnx.py
```

Run the simulator replay with:

```bash
python3 scripts/run_projection_stack_aimc_simulator_payloads.py
```

The replay extracts the ONNX initializers, computes a digital reference, sends only the four MatMul operators through AIHWKIT and CrossSim, keeps Add and Relu digital, then writes strict simulator payloads.

The output files are:

- `evidence/aimc-simulator-adapters/aihwkit-projection-stack-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-projection-stack-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/projection-stack-simulator-payload-run-summary.json`

## Evidence

The current result is split:

- CrossSim runs the projection-stack weights and passes the positive-evidence guard.
- AIHWKIT runs the projection-stack weights but exceeds the residual threshold, so the guard rejects it for a positive claim.

That split is useful. It says the pipeline is working as an evidence system, not only as a demo. A simulator run can be accepted, or it can be rejected when the numeric output is outside the claim boundary.

## Allowed Claim

The system can say:

CrossSim now runs a strict simulator payload for a larger four-MatMul ONNX projection-stack fixture with real initializer weights, and that payload passes the guarded evidence importer. AIHWKIT also runs the same projection-stack replay, but the current payload is rejected for a positive simulator claim because its residual is above the local threshold.

## Refused Claim

The system cannot say:

- a pretrained foundation model has been simulated
- attention or softmax has been simulated
- token accuracy has been measured
- device drift has been calibrated
- board latency has been measured
- board power has been measured
- analog macro layout has been verified
- the design is ready for tapeout

## Next Handoff

The next proof is an attention-shaped graph.

That graph should add the missing foundation-model stress points: Q/K score formation, softmax or a bounded substitute, value mixing, output projection, normalization boundary, and repeated token steps. The same rule should hold: analog only gets the static-weight projection work unless there is separate evidence for a dynamic operation.
