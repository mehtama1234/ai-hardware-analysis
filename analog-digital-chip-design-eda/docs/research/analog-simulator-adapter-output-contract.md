# Analog Simulator Adapter Output Contract

This page defines what a real AIHWKIT or CrossSim adapter must write before its result can strengthen the analog evidence.

The point is simple:

A simulator name is not evidence. A simulator run is evidence only when the output says what object was simulated, what physical assumptions were used, what changed in the result, and what claim is still blocked.

## Object

The object is a normalized `analog_error_simulation` evidence payload.

It is the file that moves a simulator result into the old backend claim-readiness system.

The payload must describe the same object the reviewer cares about:

- a model layer
- a matrix-vector operation
- a crossbar tile case
- a converter setting
- a local residual or accuracy delta

If the simulator runs on a different object, the result may be useful for learning, but it cannot prove the selected package claim.

## Constraint

Analog simulation can hide the important parts.

The same model can look safe or unsafe depending on:

- ADC bits
- DAC bits
- array size
- bit slicing
- read noise
- write noise
- drift
- row voltage drop
- column current range
- temperature assumption
- voltage assumption

So the payload must expose those assumptions. If the assumptions are hidden, the backend should treat the result as too weak for a stronger simulator claim.

## Design Move

The adapter writes one JSON object that follows:

`sources/evidence/analog-simulator-adapter-output-schema.json`

The payload must contain:

- `error_model`: the simulator, target object, converter settings, residual, and analog assumptions
- `temperature_range`: the temperature sweep or fixed-temperature boundary
- `voltage_range`: the voltage sweep or fixed-voltage boundary
- `accuracy_impact`: the estimated output or task change
- `calibration_profile`: the named profile that makes assumptions visible
- `provenance`: the tool name, tool version, artifacts, and claim boundary

For AIHWKIT, the target object should be a model layer or small network with explicit analog device assumptions.

For CrossSim, the target object should be a matrix-vector or crossbar case with explicit array and converter assumptions.

## Evidence

A valid payload can pass the old backend strict tool path only when:

- the tool name contains AIHWKIT, CrossSim, SPICE, ngspice, Xyce, or a named calibrated simulator
- `accuracy_impact.pass` is true
- `calibration_profile` is present
- ADC and DAC bits are present
- the temperature boundary is present
- the voltage boundary is present
- provenance says whether this is measured silicon or not

The current local strict payload passes because it is a bounded ngspice/local nonideality fixture.

The current AIHWKIT/CrossSim adapter status does not pass as simulator evidence because both external tools are skipped.

## Allowed Claim

The system can say:

This schema defines the minimum information needed before an AIHWKIT or CrossSim run can become strict analog simulator evidence.

If a real adapter run produces this payload and the backend accepts it, the system can say the selected analog object has bounded simulator evidence under the stated assumptions.

## Refused Claim

The system cannot say:

- a skipped adapter is simulator evidence
- a smoke import alone proves task accuracy
- analog simulator evidence proves board latency
- analog simulator evidence proves measured power
- analog simulator evidence proves calibrated silicon unless the payload says `measurement_level` is `calibrated_silicon`
- analog simulator evidence proves production readiness

## Next Handoff

The next implementation step is to make `scripts/check_aimc_simulator_adapters.py` write a second file when a tool is available:

- `evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json`
- or `evidence/aimc-simulator-adapters/crosssim-analog-error-simulation.json`

That file should then be validated against the backend strict tool readiness path before it is imported.

The guarded command is:

```bash
python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json
```

By default this validates only. It does not import.

To import a real payload, the command must be run with `--import`.

Dry-run payloads are refused:

```bash
python3 scripts/import_analog_simulator_payload.py --expect-reject evidence/aimc-simulator-adapters/dry-run/aihwkit-analog-error-simulation.dry-run.json
```

The import path is explained in `guarded-simulator-payload-import.md`.

Until a tool actually runs, the current skipped-state report remains the correct result.
