# Optional Simulator Payload Run Path

This page explains the step after installing AIHWKIT or CrossSim.

The important question is no longer "is the package installed?" The important question is "did the tool run on a named object and write evidence that the backend can judge?"

## Object

The object is a strict simulator payload produced by an optional external simulator adapter:

- `evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-analog-error-simulation.json`

Each file must describe the model layer or crossbar case, the converter assumptions, the residual, the baseline, the simulated output, and the claim boundary.

## Constraint

A real run has to clear three separate bars.

First, the Python package must be importable.

Second, the adapter must execute a concrete fixture. A package import alone is not a run.

Third, the output must satisfy the strict payload contract and the guarded backend importer.

## Design Move

Run:

```bash
python3 scripts/run_optional_aimc_simulator_payloads.py
```

The script writes:

```text
evidence/aimc-simulator-adapters/optional-simulator-payload-run-summary.json
```

If AIHWKIT is missing, its result is `skipped`.

If CrossSim is missing, its result is `skipped`.

If a tool is importable and its small fixture runs, the script writes the matching strict payload path.

That payload still must be checked:

```bash
python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json
```

or:

```bash
python3 scripts/import_analog_simulator_payload.py evidence/aimc-simulator-adapters/crosssim-analog-error-simulation.json
```

## Evidence

The current optional simulator environment can import AIHWKIT and CrossSim.

The current run path writes small-fixture payloads for both tools. That is useful because it proves the tools can execute and the payloads can be checked. It still refuses to treat a small fixture as full model, board, silicon, or production evidence.

When a payload is written, the evidence is still narrow: a small external simulator fixture ran. That can strengthen bounded simulator evidence for that fixture, not for the whole analog foundation-model chip.

## Allowed Claim

The system can say:

The lab has a run path that can turn an installed AIHWKIT or CrossSim module into a strict simulator payload, and it records skipped or failed tools without upgrading claims.

## Refused Claim

The system cannot say:

- a package import is simulator evidence
- a small fixture proves full model accuracy
- a simulator payload proves board latency or power
- a simulator payload proves calibrated silicon
- a simulator payload proves layout, signoff, packaging, reliability, or tapeout readiness

## Next Handoff

After installing optional simulators, run the payload generator and validate any written payload in validate-only mode.

Only then should the payload be imported into the old backend.
