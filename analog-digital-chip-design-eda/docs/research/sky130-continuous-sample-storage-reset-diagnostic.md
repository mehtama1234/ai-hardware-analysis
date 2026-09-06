# Sky130 Continuous SAR Sample-Storage Reset Diagnostic

The continuous SAR probe showed that the comparator storage nodes retained a
large prior-cycle differential. A matched reset network was therefore added
to return `sp` and `sn` toward `VDD/2` before each retained-bit sample. The
branch is selected with `AIMC_CONTINUOUS_SAMPLE_RESET=1` and is not enabled by
default.

## Results

A one-conversion run removed the illegal bottom-plate excursion and increased
the code-2 third-cycle preamp margin from approximately `20 mV` to
`194 mV`, but still resolved code 1 instead of code 2. A stiff reset switch
also caused repeated-transient convergence failures. A gentler version using
`1 um` reset devices, `100 kOhm` matched series resistance, and a `3.5 ns`
reset window completed all five conversions, but produced:

| Expected | Final | Bottom plates |
|---:|---:|---|
| 0 | 7 | pass |
| 2 | 10 | fail |
| 4 | 11 | fail |
| 6 | 14 | fail |
| 7 | 15 | fail |

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-sample-reset-code2-diagnostic.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-sample-reset-100k-full-diagnostic.json`

## Decision

The reset branch is rejected as an acceptance candidate. It proves that stale
sample memory contributes to the original failure, but directly forcing the
existing `sp`/`sn` storage nodes to a fixed common mode destroys the intended
DAC/reference sampling relationship. The next physical revision must use a
dedicated isolated sample-and-copy stage, with explicit charge-transfer and
common-mode measurements, instead of resetting the comparator storage nodes
in place.
