# AIMC Simulator Adapter Status

This report checks whether AIHWKIT or CrossSim can produce stronger analog simulator evidence for the current AIMC proof slice.

Run-output contract: `sources/evidence/analog-simulator-adapter-output-schema.json`.

## Result

- AIHWKIT: available (python module importable)
- CrossSim: available (python module importable)
- analog candidates: 3
- local residual: 0.090004
- AIHWKIT future payload: `evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json`
- CrossSim future payload: `evidence/aimc-simulator-adapters/crosssim-analog-error-simulation.json`
- AIHWKIT smoke: ran
- CrossSim smoke: ran

## Claim Boundary

the simulator adapter boundary was checked and tool availability or missing-tool state was recorded without upgrading broad claims

do not call availability smoke checks calibrated silicon, measured board runtime, measured power, physical signoff, or production readiness

## Candidate Comparison

| Layer | Local residual | AIHWKIT | CrossSim | Claim effect |
| --- | ---: | --- | --- | --- |
| measured_fixed_projection_tile | 0.090004 | availability smoke ran; strict payload still required | availability smoke ran; strict payload still required | external simulator payload is required before this candidate receives stronger simulator evidence |
| backend_dense1.matmul | 0.090004 | availability smoke ran; strict payload still required | availability smoke ran; strict payload still required | external simulator payload is required before this candidate receives stronger simulator evidence |
| backend_dense2.matmul | 0.090004 | availability smoke ran; strict payload still required | availability smoke ran; strict payload still required | external simulator payload is required before this candidate receives stronger simulator evidence |

## Next Handoff

run the optional simulator payload exporter, validate any real payload, then import only if the guarded importer accepts it
