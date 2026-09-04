# Tensor-Shaped Simulator Evidence

This page explains the stronger AIHWKIT and CrossSim replay.

The earlier workload replay used one compact 4x4 example and tied it to the backend-selected analog candidates. This replay keeps the backend operator chain shape itself.

## Object

The object is the two analog `MatMul` operators selected by the restored backend hardware placement:

- `dense1.matmul` with declared output shape `[1,3]`
- `dense2.matmul` with declared output shape `[1,2]`

The replay treats the chain as:

- `dense1.matmul`: 4 inputs to 3 outputs
- `dense2.matmul`: 3 inputs to 2 outputs

That is the first useful shape proof. The tensor sizes come from the backend placement artifact, and the second layer input width comes from the first layer output width.

## Constraint

The local backend placement artifact does not include trained package weights.

Because of that, this replay uses deterministic fixture weights and inputs keyed by the candidate ID. This is still useful because it proves the tool path can execute the right operator shapes and write strict payloads. It is not a model accuracy result.

## Design Move

Run:

```bash
python3 scripts/run_tensor_shape_aimc_simulator_payloads.py
```

The script reads:

- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/backend-hardware-placement.json`

It keeps only rows where:

- `operator_kind` is `MatMul`
- `placement` is `analog`
- `analog_candidate` is `true`

For each row, it builds a deterministic matrix and input vector, runs the matrix-vector operation through AIHWKIT and CrossSim, compares each simulator output with the digital result, and writes strict simulator payloads.

The output files are:

- `evidence/aimc-simulator-adapters/aihwkit-tensor-shape-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-tensor-shape-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/tensor-shape-simulator-payload-run-summary.json`

Each payload must pass:

```bash
python3 scripts/import_analog_simulator_payload.py <payload.json>
```

## Evidence

This proves a narrow but real thing.

The backend can identify analog matrix operators. The hardware lab can read those operators. AIHWKIT and CrossSim can run matrix-vector payloads at the operator chain shapes. The guarded importer accepts the resulting payloads under the same schema used for strict analog simulator evidence.

The main residual is the largest per-candidate relative L2 difference between the digital matrix-vector output and the simulator output.

## Allowed Claim

The system can say:

AIHWKIT and CrossSim now run strict simulator payloads for the backend analog MatMul candidate tensor shapes, and those payloads pass the guarded evidence importer.

## Refused Claim

The system cannot say:

- this tensor-shaped fixture page simulated the trained package weights
- the full model graph was simulated end to end
- the result predicts token accuracy
- the result is calibrated to silicon
- the result proves board latency or board power
- the result proves analog macro layout or tapeout readiness

## Next Handoff

The next improvement after this page is trained-weight replay.

That requires the backend package to expose or export the actual weights for `dense1.matmul` and `dense2.matmul`. Once those weights exist locally, the same script can stop generating deterministic fixtures and can replay the real package tensors.
