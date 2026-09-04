# Sky130 Sampled Internal Decision-Cap Latch Candidate

- status: `sampled_internal_decision_cap_latch_candidate_characterized_not_accepted`
- case count: `4`
- measured case count: `0`
- timed-out case count: `4`
- passing setting count: `0`
- half LSB 12b V: `2.197265625e-04`
- prior best kickback V: `6.578530000e-04`
- accepted post-layout written: `False`

## First Principle

The sampled value is stored as charge. If the latch input is tied directly to that stored charge, the latch clock can push charge back and change the value being decided.

This candidate copies the value onto a smaller internal decision capacitor before latch regeneration. The original sampled node should then be less exposed to the latch clock. The candidate is useful only if the copied internal node still gives the latch enough sign while sampled-node kickback falls below half-LSB.

## Setting Summary

| decision cap F | measured | resolved | kickback pass | worst kickback V | min output diff V |
|---:|---:|---:|---:|---:|---:|
| `2.000000000e-14` | `0` | `0` | `0` | `not measured` | `not measured` |
| `5.000000000e-14` | `0` | `0` | `0` | `not measured` | `not measured` |

## Boundary

does not prove noise, offset statistics, SAR bit cycling, extracted layout, DRC/LVS, or accepted post-layout converter evidence
