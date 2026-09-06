# Sky130 Continuous SAR Two-Phase Sample/Latch Diagnostic

This branch combines the capacitive sample-copy interface with an explicit
preamp-tail enable. The intended sequence is: DAC redistribution and sample
while the preamp is quiet, copied differential settling, preamp amplification,
then latch regeneration. It is selected with
`AIMC_CONTINUOUS_CAPACITIVE_COPY=1` and
`AIMC_CONTINUOUS_PREAMP_PHASE_GATE=1`.

## Result

The one-conversion run is electrically measurable and retains legal bottom
plates, but expected code 2 still resolves as code 1. The complete replay
finishes with this map:

| Expected | Final | Bottom plates |
|---:|---:|---|
| 0 | 7 | pass |
| 2 | 10 | fail |
| 4 | 11 | fail |
| 6 | 11 | fail |
| 7 | 11 | fail |

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-two-phase-copy-code2-diagnostic.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-two-phase-copy-nmos64-bank8-full-diagnostic.json`

## Decision

The simple preamp-tail gate is rejected. It does not preserve the repeated
SAR state and makes the later conversions worse. A valid next revision needs
explicit non-overlapping sample, copy, preamp, and latch phases with state
reset designed into the comparator cell; adding a gate around the existing
tail is not sufficient.
