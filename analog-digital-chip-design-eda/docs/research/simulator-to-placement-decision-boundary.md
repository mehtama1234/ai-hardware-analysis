# Simulator To Placement Decision Boundary

This page explains the handoff from AIHWKIT and CrossSim results to analog placement.

The core idea is simple: a simulator result is not a placement decision. A simulator result says what happened under one stated set of assumptions. A placement decision says whether one operator in one model is allowed to request analog service. The system must join those two things carefully.

## Object

The object is one backend operator plus one simulator source.

For the current package, the backend operator list is small:

- `dense1.matmul`
- `dense1.bias`
- `dense1.relu`
- `dense2.matmul`
- `dense2.bias`

Only `dense1.matmul` and `dense2.matmul` are shaped like analog array work. They are fixed-weight matrix multiplies. A fixed weight can be stored as conductance. An input vector can be applied as row values. The output is a set of column sums.

That shape match is necessary, but it is not enough.

The simulator source must also describe the same kind of work. A CrossSim result from fixed-weight MatMuls can be used as evidence for fixed-weight MatMul placement. It cannot be used as evidence for softmax, dynamic attention score formation, bias addition, activation, residual addition, scheduling, or board power.

## Constraint

Analog placement has two separate questions.

First: can the operation be expressed as analog array work?

Second: after nonideal analog behavior is included, is the error small enough for this model path?

The first question is structural. The second question is evidential.

If those questions are merged, the system will overclaim. A MatMul may fit an array and still be too sensitive to analog error. A simulator may run and still produce too much residual. A JSON payload may be shaped correctly and still fail the backend strict-tool rule. A passing attention-projection result may be the wrong source for a dense MLP row if a closer dense-MLP source exists.

## Design Move

The bridge separates the decisions into gates.

Gate 1: structural placement.

The backend marks each model operator as analog, digital, or fallback based on its operation kind and shape.

Gate 2: simulator payload readiness.

AIHWKIT and CrossSim payloads must come from real runs, name their array and device assumptions, compare against a digital reference, and pass the strict payload contract.

Gate 3: positive-claim threshold.

If the residual is above the allowed boundary, the payload may still be useful as a warning, but it cannot support a positive analog claim.

Gate 4: source matching.

The accepted simulator source must match the operator family. The current policy is `fixed_weight_matmul_family_match`. Dense fixed-weight MatMul rows use the calibrated deep transformer-MLP stack as the closest available source. The one-block transformer-MLP source is the fallback. Attention-projection evidence is kept as a general projection fallback, not the first source for dense MLP rows.

Gate 5: residual-aware placement.

Only after the previous gates pass can a structural analog candidate remain `analog_allowed`.

## Evidence

The current proof chain gives this result:

- AIHWKIT is installed and runs the fixture family.
- CrossSim is installed and runs the same fixture family.
- The guarded importer accepts only strict payloads that pass the backend evidence rule.
- Several larger AIHWKIT payloads run but are rejected from positive claims because their residual is too high.
- CrossSim calibrated fixed-weight MatMul payloads pass the current positive boundary.
- The residual-aware placement step chooses `deep_transformer_mlp_stack` as the source for the two backend MatMul rows.
- The two MatMul rows remain analog-allowed.
- The bias and ReLU rows remain digital.

The result is not "CrossSim passed, therefore the model is analog." The result is narrower: two fixed-weight MatMul rows are allowed to request analog service because their structural shape and accepted calibrated simulator source match under the current local policy.

## Allowed Claim

The system can say:

The current backend placement is filtered by simulator evidence before analog service is allowed. Fixed-weight MatMul rows remain analog-allowed only when an accepted calibrated simulator source matches their operation family and stays inside the local residual boundary.

## Refused Claim

The system cannot say:

- every model operator can run on analog
- every MatMul is safe for analog
- AIHWKIT and CrossSim agree on the whole model
- a threshold-fail simulator payload supports a positive analog claim
- attention evidence proves dense MLP placement when a closer dense MLP source exists
- simulator evidence proves measured board latency
- simulator evidence proves measured energy
- simulator evidence proves analog macro layout
- simulator evidence proves calibrated silicon
- simulator evidence proves tapeout readiness

## Next Handoff

The next stronger proof is not a broader sentence. It is a better accepted source.

Useful upgrades are:

- a larger real-model ONNX slice whose fixed-weight MatMuls pass the same guarded importer
- an AIHWKIT mapping whose residual stays inside the positive-claim boundary
- a CrossSim layout-risk adapter that exposes array size, wire assumptions, ADC range, DAC precision, bit slicing, and column-current range
- a measured board runtime trace tied to the same package, workload, board, and runtime trace ID
- a measured power trace tied to that same runtime trace ID and time window

Until those exist, the current system should keep saying exactly what it proves: bounded local simulator-backed placement for selected MatMul rows, with board, power, silicon, layout, and production claims still held back.
