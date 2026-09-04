# Workload-Shaped Simulator Evidence

This page explains the next step after small AIHWKIT and CrossSim fixtures.

The small fixtures prove that the tools run. The workload-shaped replay asks a stronger question: can those tools run on the same analog candidates selected by the backend placement and governor path?

## Object

The object is the backend-selected analog candidate set:

- `measured_fixed_projection_tile`
- `backend_dense1.matmul`
- `backend_dense2.matmul`

The replay uses a compact 4x4 matrix-vector case because the local analog nonideality stack already records a four-output ideal path and final analog path.

The output files are:

- `evidence/aimc-simulator-adapters/aihwkit-workload-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-workload-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/workload-simulator-payload-run-summary.json`

## Constraint

The stronger object does not make this a full model result.

It proves that AIHWKIT and CrossSim can run a compact replay tied to the selected analog matmul candidates. It does not prove the full tensor shapes, long-context behavior, token accuracy, board runtime, measured power, or silicon calibration.

## Design Move

Run:

```bash
python3 scripts/run_workload_aimc_simulator_payloads.py
```

The script reads:

- `model-impact-governor-requests.csv`
- `analog-nonideality-stack.csv`

It keeps only rows that are analog candidates and pass the governor.

Then it runs the same 4x4 matrix-vector replay through AIHWKIT and CrossSim, compares the simulator output with the ideal digital output, and writes strict simulator payloads.

Each payload must still pass:

```bash
python3 scripts/import_analog_simulator_payload.py <payload.json>
```

## Evidence

The evidence is stronger than a smoke test because the named object comes from the actual placement/governor flow.

The evidence is weaker than a real model benchmark because the replay is compact. It uses the existing four-output fixture as the bridge object.

The useful fact is the agreement boundary:

- ideal digital output is the reference
- local nonideality output is the existing lab boundary
- AIHWKIT output is one external simulator view
- CrossSim output is another external simulator view
- the final residual is the larger of local residual and simulator residual

## Allowed Claim

The system can say:

AIHWKIT and CrossSim now run workload-shaped compact replays tied to backend-selected analog matmul candidates, and their payloads can be checked by the same guarded importer used for strict analog evidence.

## Refused Claim

The system cannot say:

- the full transformer has been simulated in AIHWKIT or CrossSim
- the analog macro layout has been simulated
- the result is calibrated to silicon
- the result proves board latency or board power
- the result proves production readiness

## Next Handoff

The next improvement after this page is the tensor-shaped replay for `dense1.matmul` and `dense2.matmul`.

That means the adapter should read the model graph dimensions, build the matching matrices, preserve the same candidate IDs, and compare simulator output against the backend's digital reference for those exact shapes.
