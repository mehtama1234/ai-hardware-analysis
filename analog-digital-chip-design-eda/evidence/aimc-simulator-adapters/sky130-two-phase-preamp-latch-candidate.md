# Sky130 Two-Phase Preamp-Then-Latch Candidate

- status: `two_phase_preamp_latch_candidate_passed_schematic_not_noise_layout_or_strict`
- case count: `2`
- measured case count: `2`
- timed-out case count: `0`
- resolved correct polarity count: `2`
- kickback below half LSB count: `2`
- worst sampled differential kickback V: `1.970000000e-05`
- minimum preamp diff before latch V: `7.466000000e-04`
- all cases pass: `True`
- accepted post-layout written: `False`

## First Principle

A regenerative latch is violent because it uses positive feedback. A preamp-then-latch design separates the quiet part from the violent part. The preamp first turns the small sampled difference into a larger internal difference. Only after that does the latch regenerate.

This candidate is useful only if the latch still resolves both signs and the latch clock no longer moves the original sampled nodes beyond the half-LSB line.

## Results

| case | measured | kickback V | preamp diff before latch V | output diff V | resolved | kickback pass |
|---|---:|---:|---:|---:|---|---|
| `negative_target_edge` | `True` | `1.970000000e-05` | `-7.466000000e-04` | `1.371086500e+00` | `True` | `True` |
| `positive_target_edge` | `True` | `1.970000000e-05` | `7.466000000e-04` | `-1.371086500e+00` | `True` | `True` |

## Boundary

does not prove noise, offset statistics, SAR bit cycling, extracted layout, DRC/LVS, or accepted post-layout converter evidence
