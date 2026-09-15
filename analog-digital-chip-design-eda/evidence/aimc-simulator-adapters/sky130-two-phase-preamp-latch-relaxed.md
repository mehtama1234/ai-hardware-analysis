# Sky130 Two-Phase Preamp-Then-Latch Candidate

- status: `two_phase_preamp_latch_candidate_characterized_not_accepted`
- case count: `2`
- measured case count: `0`
- timed-out case count: `2`
- resolved correct polarity count: `0`
- kickback below half LSB count: `0`
- worst sampled differential kickback V: `not measured`
- minimum preamp diff before latch V: `not measured`
- all cases pass: `False`
- accepted post-layout written: `False`

## First Principle

A regenerative latch is violent because it uses positive feedback. A preamp-then-latch design separates the quiet part from the violent part. The preamp first turns the small sampled difference into a larger internal difference. Only after that does the latch regenerate.

This candidate is useful only if the latch still resolves both signs and the latch clock no longer moves the original sampled nodes beyond the half-LSB line.

## Results

| case | measured | kickback V | preamp diff before latch V | output diff V | resolved | kickback pass |
|---|---:|---:|---:|---:|---|---|
| `negative_target_edge` | `False` | `not measured` | `not measured` | `not measured` | `False` | `False` |
| `positive_target_edge` | `False` | `not measured` | `not measured` | `not measured` | `False` | `False` |

## Boundary

does not prove noise, offset statistics, SAR bit cycling, extracted layout, DRC/LVS, or accepted post-layout converter evidence
