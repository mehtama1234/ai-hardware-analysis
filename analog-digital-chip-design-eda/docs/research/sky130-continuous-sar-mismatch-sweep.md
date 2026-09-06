# Sky130 Continuous SAR Mismatch Qualification

This page documents the full-loop mismatch runner at
`scripts/run_sky130_continuous_mismatch_sweep.py`. Unlike the earlier isolated
DAC mismatch experiments, each trial invokes the four-cycle continuous SAR and
checks all five representative conversions.

## Current result

The first smoke population exposed a harness error: it replaced the promoted
`0.75x` bit-1 trim with a value near `1.0x`. Those results are retained as a
debug artifact but are not qualification evidence. The runner now applies
independent Gaussian perturbations around the actual promoted base scales
`[1.0, 0.75, 1.0, 1.0]`; the separate `1.5x` LSB trim remains enabled.

The corrected pre-reset population uses a fixed seed of `130` and `1.0%`
sigma. Its full 100-trial result is retained as a baseline: `95/100`
full-map/legal passes, `97/100` complete measured transients, and three
simulation failures.

The promoted design adds a matched sample-storage reset (`3.5 ns` reset,
`10 kOhm` series resistance) and was rerun over the identical seeded
population. The reset-promoted result is `90/100` full-map passes and `96/100`
legal-bottom-plate passes; `96/100` trials produced a measured transient and
four terminated before a complete measurement. The six measured map failures
all returned `7,9,10,12,14` rather than `0,2,4,6,7`. This is a measured
schematic-level stress result, not a foundry-yield claim, and it does not
replace the nominal or PVT gates.

A focused replay showed that increasing the reset width to `5.0 ns` can fix
some individual failed instances, so it was tested across the same complete
population as a negative control. That run produced only `83/100` full-map
passes and `94/100` legal-bottom-plate passes, with `94/100` complete
transients. It is rejected as the default timing and retained at
`evidence/aimc-simulator-adapters/sky130-continuous-physical-sar-mismatch-reset5ns-100.json`.

| trial | effective capacitor scales (MSB to LSB) | returned map | bottom plates legal |
| ---: | --- | --- | --- |
| 0 | 0.99207, 0.74926, 0.99897, 0.98215 | 0, 2, 4, 6, 7 | yes |
| 1 | 0.99873, 0.74874, 1.00057, 1.00907 | 0, 2, 4, 6, 7 | yes |
| 2 | 1.01449, 0.74837, 0.98535, 0.99732 | 0, 2, 4, 6, 7 | yes |

The initial, invalid smoke rows were:

| trial | capacitor scales (MSB to LSB) | returned map | bottom plates legal |
| ---: | --- | --- | --- |
| 0 | 0.99207, 0.99901, 0.99897, 0.98215 | 7, 10, 11, 13, 14 | no |
| 1 | 0.99873, 0.99832, 1.00057, 1.00907 | 0, 2, 3, 5, 6 | yes |
| 2 | 1.01449, 0.99783, 0.98535, 0.99732 | 0, 2, 3, 5, 6 | yes |

The expected map is `0, 2, 4, 6, 7`. The fixed-trim candidate therefore has a
measured stress pass fraction of `95%` under this declared model, but this is
not a foundry mismatch-yield claim.

## Engineering consequence

The reset addresses the earlier repeatable first-conversion charge-state
failure, but it does not close mismatch qualification: the remaining measured
failures share a shifted decision sequence, while four cases still fail to
produce a complete transient. The next design decision is to improve
reset/common-mode settling and decision margin, or add per-instance capacitor
calibration that updates references/trim. Any repair must be replayed across
the same full population and compared against all retained populations. The
current default remains the `3.5 ns` reset because it has the stronger
complete-population result.

## Claim boundary

The runner is a reproducible closed-loop stress test, not foundry Monte Carlo.
It establishes a retained 95/100 pre-reset baseline and a 90/100
reset-promoted full-map result, and a rejected `5 ns` negative-control result
for the declared capacitor-variation model, not production yield. Comparator
offset/noise, extracted-layout behavior, DRC/LVS signoff, board behavior, and
silicon acceptance remain unproven.
