# Sky130 Source-Follower Isolated Latch Candidate

- status: `source_follower_isolated_latch_candidate_characterized_not_accepted`
- case count: `4`
- measured case count: `0`
- timed-out case count: `4`
- passing setting count: `0`
- half LSB 12b V: `2.197265625e-04`
- prior best kickback V: `6.578530000e-04`
- accepted post-layout written: `False`

## First Principle

The latch should see the decision voltage without forcing its clock movement back into the sampled nodes. A source follower tries to do that by making the sampled node drive only a gate while a separate source node drives the latch input.

This is useful only if both facts hold together: both signs still resolve, and sampled-node kickback falls below the half-LSB line.

## Setting Summary

| follower W um | bias uA | measured | resolved | kickback pass | worst kickback V | min output diff V |
|---:|---:|---:|---:|---:|---:|---:|
| `0.42` | `1.0` | `0` | `0` | `0` | `not measured` | `not measured` |
| `1.0` | `2.0` | `0` | `0` | `0` | `not measured` | `not measured` |

## Boundary

does not prove noise, offset statistics, SAR bit cycling, extracted layout, DRC/LVS, or accepted post-layout converter evidence
