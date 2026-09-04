# Guarded Simulator Payload Import

This page explains the last step before a real AIHWKIT or CrossSim result can enter the backend.

The rule is simple:

A simulator payload may be shaped correctly and still not be proof. The importer must check whether it came from a real run, whether it satisfies the adapter contract, and whether the backend agrees that it is strict simulator evidence.

## Object

The object is one JSON file:

- `evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json`
- or `evidence/aimc-simulator-adapters/crosssim-analog-error-simulation.json`

That file is supposed to become `analog_error_simulation` evidence.

It is not imported directly by copying it into the evidence folder. It goes through:

```bash
python3 scripts/import_analog_simulator_payload.py <payload.json>
```

By default, the command validates only. It does not import.

## Constraint

There are three ways this can go wrong.

First, the file may be only a dry-run example. A dry-run payload can show the shape, but it did not come from AIHWKIT or CrossSim actually running.

Second, the file may omit the physical assumptions. Without ADC bits, DAC bits, device assumptions, array assumptions, temperature boundary, and voltage boundary, the result is too vague.

Third, the file may pass local shape checks but fail the backend strict-tool rule. The backend is the claim gate, so its answer is the one that matters before import.

## Design Move

The guarded importer checks the payload in this order:

1. reject `dry_run: true`
2. check the local adapter output contract
3. check the old backend `analog_error_simulation` structure
4. check backend strict-tool readiness
5. import only when `--import` is explicitly passed

The validation-only command is:

```bash
python3 scripts/import_analog_simulator_payload.py evidence/aimc-hardware-lab/analog_error_simulation_strict_tool.json
```

The validation command for the current AIHWKIT payload is:

```bash
python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json
```

The validation command for the current CrossSim payload is:

```bash
python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/crosssim-analog-error-simulation.json
```

The import command for a real payload is:

```bash
python3 scripts/import_analog_simulator_payload.py --import evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json
```

The rejection check is:

```bash
python3 scripts/import_analog_simulator_payload.py --expect-reject evidence/aimc-simulator-adapters/dry-run/aihwkit-analog-error-simulation.dry-run.json
```

## Evidence

The bridge now runs the guarded importer as one of its proof gates.

Current result:

- the strict ngspice/local nonideality payload passes validate-only mode
- the AIHWKIT small-fixture payload passes validate-only mode
- the CrossSim small-fixture payload passes validate-only mode
- the AIHWKIT workload-shaped payload passes validate-only mode
- the CrossSim workload-shaped payload passes validate-only mode
- the AIHWKIT tensor-shaped payload passes validate-only mode
- the CrossSim tensor-shaped payload passes validate-only mode
- the AIHWKIT trained-weight payload is rejected for a positive claim because its residual is above the local threshold
- the CrossSim trained-weight payload passes validate-only mode
- the AIHWKIT projection-stack payload is rejected for a positive claim because its residual is above the local threshold
- the CrossSim projection-stack payload passes validate-only mode
- the AIHWKIT transformer-MLP-block payload is rejected for a positive claim because its residual is above the local threshold
- the CrossSim transformer-MLP-block payload passes validate-only mode
- the AIHWKIT calibrated transformer-MLP-block payload is rejected for a positive claim because its residual is above the local threshold
- the CrossSim calibrated transformer-MLP-block payload passes validate-only mode
- the AIHWKIT attention-block payload is rejected for a positive claim because its residual is above the local threshold
- the CrossSim attention-block payload passes validate-only mode
- the AIHWKIT calibrated attention-block payload is rejected for a positive claim because its residual is above the local threshold
- the CrossSim calibrated attention-block payload passes validate-only mode
- the dry-run AIHWKIT payload is rejected
- no dry-run file is imported
- no availability-only AIHWKIT or CrossSim check becomes simulator proof

## Allowed Claim

The system can say:

The lab has a guarded path for simulator evidence. The current AIHWKIT and CrossSim small-fixture, workload-shaped, and tensor-shaped payloads pass validate-only mode. The CrossSim trained-weight, projection-stack, transformer-MLP-block, calibrated transformer-MLP-block, attention-block, and calibrated attention-block payloads also pass. The AIHWKIT trained-weight, projection-stack, transformer-MLP-block, calibrated transformer-MLP-block, attention-block, and calibrated attention-block payloads run but are rejected for positive claims because their residuals are above the local threshold. Any real payload must pass the local contract and backend strict-tool readiness before it can be imported.

## Refused Claim

The system cannot say:

- the dry-run payload is simulator evidence
- an AIHWKIT availability check is simulator evidence
- a CrossSim availability check is simulator evidence
- a correctly shaped JSON file proves the model unless it came from a real run
- simulator evidence proves measured latency, measured power, calibrated silicon, or production readiness

## Next Handoff

The next real implementation step is calibration or a better analog mapping for the attention-shaped replay.

Before expecting those calibrated payloads, run:

```bash
./scripts/check_tools.sh
```

That command now reports whether the `aihwkit` Python module or a CrossSim-style Python module is importable.

That real payload must be validated first without `--import`.

Only after the validation-only command passes should it be imported with `--import`.
