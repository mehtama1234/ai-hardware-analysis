# Board And Power Measurement Boundary

This page defines the line between a local runtime or power estimate and a measured hardware claim.

The question is:

What must be recorded before the workbench can say the model ran on hardware with measured latency, energy, and thermal behavior?

The answer is not "a board was involved" or "a power number exists." The answer is a synchronized record of one workload window: the same package, same runtime, same start time, same end time, same power samples, same thermal setup, and the same host-overhead rule.

## Workflow Contract

Consumes: package ID, model configuration, backend hardware placement, governor trace, board runtime trace, voltage and current samples, meter setup, thermal setup, workload ID, and host-overhead boundary.

Produces: measured `board_runtime`, measured `power_thermal`, synchronized latency and energy window, setup record, repeated-run summary, uncertainty statement, and claim-readiness update.

Supports: measured latency or measured energy claims only for the exact board, firmware, package, workload, measurement setup, and run window recorded.

Refuses: general chip performance, production readiness, analog macro proof, silicon calibration proof, signoff power, or claims that combine unrelated runtime and power estimates.

## Current State

The current `board_runtime.json` is useful, but it is not a board measurement.

It records:

- `board_id`: `local-rtl-simulation-not-board`
- runtime mode: local RTL simulation
- latency: `1.675 ms`
- trace events: 10
- fallback events: 6
- RTL checker: passed
- Yosys synthesis context: present
- OpenLane context: present

That supports a local control-path discussion. It does not prove measured board latency.

The current `power_thermal.json` is useful, but it is not measured power.

It records:

- meter: none
- supply voltage: not measured
- sampling rate: not sampled
- power source: OpenLane-derived control-block estimate
- temperature source: room-temperature assumption
- `not_measured_hardware`: true

That supports a needs-review energy discussion. It does not prove measured energy or measured thermal behavior.

This is why the backend keeps latency claim `C2` and energy claim `C3` in `needs review`.

## The First Principle

Latency is a time interval. Energy is accumulated electrical work over the same interval.

```text
latency = t_end - t_start
energy = integral over the run window of V(t) * I(t) dt
average_power = energy / (t_end - t_start)
```

These numbers are meaningful only when the time window is the same. A runtime trace from one run and a power estimate from another run do not prove measured energy for the workload.

The physical object being measured is not an abstract model. It is this exact chain:

```text
package
  -> board runtime
  -> firmware or host service
  -> workload start marker
  -> model execution and fallback events
  -> workload end marker
  -> voltage/current samples during the same window
  -> thermal samples and ambient condition
  -> normalized evidence record
  -> backend claim rule
```

If any link is missing, the claim must say so.

## Required Fields For A Measured Runtime Claim

To upgrade `C2`, the runtime record must identify the thing that actually ran.

Required fields:

- package ID
- model ID or workload ID
- board ID
- board revision
- firmware or runtime version
- runtime trace ID
- host service version, if the host starts the run
- backend placement artifact hash or ID
- governor configuration
- calibration profile, if analog tiles are used
- input shape, batch size, context length, or task size
- start timestamp
- end timestamp
- per-request or per-layer trace
- fallback events and reasons
- pass or fail state
- repeated-run count
- p50 and p95 latency
- excluded host setup time, if any
- included host overhead, if any

The safe statement after this exists is narrow:

```text
This package ran on this board under this setup, and the measured latency distribution for this workload was recorded.
```

It still does not prove energy, accuracy, calibration stability, or production readiness.

## Required Fields For A Measured Energy Claim

To upgrade `C3`, the power and thermal record must be tied to the same runtime window.

Required fields:

- package ID
- board ID
- workload ID
- runtime trace ID
- meter model and serial number
- measured rail or measurement point
- supply voltage samples
- current samples
- sampling rate
- time base or synchronization method
- integration start time
- integration end time
- energy over the integration window
- peak power
- average power
- host overhead included or excluded
- idle baseline rule
- ambient temperature
- board or chip temperature sensor
- thermal sampling rate
- repeated-run count
- uncertainty or error bound

The safe statement after this exists is narrow:

```text
For this measured run window, this board consumed this energy and reached this thermal state under this setup.
```

It still does not prove another board, another workload, another temperature, another package, or a production chip.

## What Not To Do

Do not multiply a local OpenLane power estimate by a local RTL runtime and call it measured energy.

Do not combine a runtime trace from one package with a power trace from another package.

Do not hide whether host overhead is included.

Do not use one demo trace as production readiness.

Do not treat a board-level measurement as chip-only power unless the measurement point isolates the chip rail.

Do not treat OpenLane cell power as measured hardware power. OpenLane-derived values can help estimate and compare local digital blocks, but they are not a meter trace.

## Claim Upgrade Rules

`C2` can move from `needs review` to `supported` only when `board_runtime` names a real board or stronger external runtime source, includes the run setup, and records repeated timing evidence.

`C3` can move from `needs review` to `supported` only when `board_runtime` and `power_thermal` describe the same workload window and the power record contains measured voltage/current samples or a clearly stronger instrumented source.

`P1` production readiness remains blocked even after measured board and power records exist. Production needs broader evidence: calibrated silicon, analog macro layout, drift over time, repeated boards, packaging, test, reliability, customer operating envelope, and signoff.

## Where This Page Fits

Previous pages:

- `aimc-evidence-ledger.md`
- `evidence-import-and-claim-readiness-first-principles.md`
- `backend-hardware-placement-first-principles.md`

Next pages:

- `measured-runtime-power-claim-upgrade-path.md`
- `cross-repo-aimc-loop-proof.md`
- `aimc-page-flow-audit.md`

The current backend claim-readiness endpoint is:

```text
http://127.0.0.1:8025/deployment-packages/pkg-e931662a01293df2/claim-readiness
```

The current hardware-lab evidence records are:

```text
evidence/aimc-hardware-lab/board_runtime.json
evidence/aimc-hardware-lab/power_thermal.json
```

This page is the contract for replacing those local records with measured records when real board or instrumented runtime data exists.

The step-by-step claim upgrade path is `measured-runtime-power-claim-upgrade-path.md`.

## Executable Boundary Check

The restored backend has a regression check for this exact line:

```text
backend/scripts/check_measured_evidence_readiness.py
```

The backend HTTP route check also covers this line:

```text
backend/scripts/check_strict_evidence_api.py
```

The check proves two things.

First, the current local hardware-lab records are structurally valid evidence, but they are not allowed to upgrade measured claims. The runtime record is rejected for measured readiness because it names `local-rtl-simulation-not-board`, carries local/not-measured provenance, and lacks measured-board provenance. The power record is rejected because it has no meter, marks `not_measured_hardware`, lacks measured voltage/current samples, and lacks measured-power provenance.

Second, the strict measured templates pass only when the payload names a board or instrumented runtime source, records repeated latency or meter samples, declares the host-overhead boundary, and carries `measured_board` or `measured_board_power` provenance.

That means the workbench can now test the difference between:

```text
ordinary evidence import:
  useful for local simulation, replay, estimates, and needs-review claims

measured evidence import:
  accepted only for board/runtime or meter-backed payloads that can support a narrow measured claim
```

This does not create measured hardware evidence. It creates the guardrail that prevents local RTL, OpenLane estimates, simulator replay, or demo traces from being mislabeled as measured board latency or measured energy.

The HTTP-level check proves the same rule through the live API shape: strict measured templates can pass `/evidence/validate-measured` or `/evidence/import-measured`, while the current local `board_runtime.json` and `power_thermal.json` are rejected by `/evidence/import-measured` with explicit reasons.

The claim-readiness check adds one more rule for `C3`. Measured runtime and measured power are not enough if they describe different work. To support measured energy, the runtime and power artifacts must agree on:

- runtime trace ID
- package ID
- workload ID
- board ID
- start time
- end time

If those fields do not match, the payloads can remain imported evidence, but the energy claim stays in `needs review`. This prevents a runtime run from one setup and a power trace from another setup from being merged into a fake energy result.

This distinction matters. Import answers one question:

```text
Is this payload a real measured artifact of its own type?
```

Claim readiness answers a stricter question:

```text
Do the measured artifacts together prove this exact claim?
```

A meter trace from another workload can be valid measured power evidence. It still cannot support energy for the current workload until it is tied to the same runtime window.

## Backend Import Shape

The restored backend now separates ordinary evidence import from measured-claim import.

Generic import remains useful for local and needs-review records:

```text
POST /evidence/import?source_id=board_runtime&package_id=...
POST /evidence/import?source_id=power_thermal&package_id=...
```

Measured-readiness validation checks the stronger board and power fields without saving the payload:

```text
POST /evidence/validate-measured?source_id=board_runtime&package_id=...
POST /evidence/validate-measured?source_id=power_thermal&package_id=...
```

Measured import saves only payloads that pass the stricter measured-readiness checks:

```text
POST /evidence/import-measured?source_id=board_runtime&package_id=...
POST /evidence/import-measured?source_id=power_thermal&package_id=...
```

If a payload is structurally valid but still says `local-rtl-simulation-not-board`, has no meter, has no measured voltage/current samples, or lacks a synchronized run window, the measured import path should reject it. That is intentional. The same payload can still be attached as local or needs-review evidence through the ordinary import path, but it must not upgrade measured latency or measured energy claims.
