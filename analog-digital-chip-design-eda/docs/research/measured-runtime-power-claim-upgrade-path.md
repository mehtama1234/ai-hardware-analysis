# Measured Runtime And Power Claim Upgrade Path

This page explains how the workbench should move from local estimates to measured latency and energy claims.

The simple rule is this: a local trace can show control behavior, and a local power estimate can show a planning number, but neither one is measured hardware evidence. A measured claim starts only when the payload records what ran, where it ran, when it ran, and how the electrical samples were tied to that same run.

## Object

The objects are claim `C2` and claim `C3`.

`C2` is the latency claim. It depends on `board_runtime`.

`C3` is the energy claim. It depends on both `board_runtime` and `power_thermal`.

These are not the same claim. A runtime trace can support a latency claim without proving energy. A power trace can be a valid measured artifact by itself and still fail to support energy if it describes a different run.

## Constraint

Latency is measured from one run window.

Energy is measured by integrating voltage and current over that same window.

```text
runtime window = start timestamp to end timestamp
instant power = voltage * current
energy = sum or integral of power over the runtime window
```

That means the backend must reject three common shortcuts.

First, it must reject local RTL runtime as measured board latency.

Second, it must reject OpenLane-derived power as measured energy.

Third, it must reject a runtime record and power record that are both measured but come from different runs.

## Design Move

The backend separates import readiness from claim readiness.

Import readiness asks:

```text
Is this payload a valid measured artifact of its own type?
```

Claim readiness asks:

```text
Do the imported artifacts together prove this exact claim?
```

For `C2`, measured runtime needs:

- package ID
- workload ID
- board ID
- board revision
- runtime version
- runtime trace ID
- latency values
- repeated-run count
- start timestamp
- end timestamp
- host-overhead boundary
- trace events
- fallback events
- measured-board or instrumented-runtime provenance

For `C3`, measured power also needs:

- the same package ID
- the same workload ID
- the same board ID
- the same runtime trace ID
- matching integration start and end timestamps
- meter or instrument source
- measured rail
- voltage samples
- current samples
- sampling rate
- average power
- peak power
- energy
- thermal samples or thermal boundary
- measured-power or instrumented-power provenance

If the power artifact is real but its runtime trace ID differs from the runtime artifact, the power artifact can be imported, but `C3` stays `needs review`.

## Current Local Evidence

The current local hardware-lab files are useful but intentionally weak:

- `board_runtime.json` records a local RTL/runtime trace, not a board run.
- `power_thermal.json` records an OpenLane-derived estimate, not meter-backed power.

So the correct current claim state is:

- `C2`: needs review
- `C3`: needs review

That is a good result. It means the workbench is refusing to convert local development evidence into measured hardware evidence.

## Positive Example

A valid measured runtime record says:

```text
this package ran this workload on this board,
under this runtime version,
with this runtime trace ID,
from this start time to this end time,
and these latency samples were recorded.
```

A valid measured power record says:

```text
this meter measured this rail on the same board,
for the same package and workload,
with the same runtime trace ID,
over the same window,
and these voltage/current samples produced this energy.
```

Only together do those records support measured energy.

## Refused Claim

The system cannot say:

- local RTL latency is measured board latency
- OpenLane power is measured hardware power
- a meter trace from one run proves energy for another run
- matching package ID alone is enough
- matching board ID alone is enough
- measured power proves accuracy
- measured latency proves energy
- measured board evidence proves calibrated silicon
- measured board evidence proves production readiness

## Executable Proof

The backend checks this boundary with:

```bash
backend/scripts/check_measured_evidence_readiness.py
backend/scripts/check_strict_evidence_api.py
```

Those checks prove the current guard behavior:

- local runtime evidence is structurally valid but not measured-ready
- local power evidence is structurally valid but not measured-ready
- strict measured runtime templates pass
- strict measured power templates pass
- matched measured runtime and power can support `C3`
- mismatched measured power keeps `C3` in `needs review`

## Next Handoff

The next real evidence upgrade is a measured pair:

1. A runtime trace from a real board or instrumented runtime source.
2. A power trace from a meter or instrumented power source.
3. The same package ID, workload ID, board ID, runtime trace ID, start time, and end time in both records.
4. Enough repeated runs to report p50 and p95 latency.
5. Voltage and current samples over the integration window.
6. A clear statement of whether host overhead is included.

After that exists, the frontend should show the narrow upgrade: measured latency and measured energy for that exact board, package, workload, and run window only. Production readiness should still remain blocked until silicon calibration, analog macro layout, reliability, thermal envelope, packaging, and signoff evidence exist.
