# Sky130 Swapped Latch Clock Timing Debug

- status: `swapped_latch_clock_timing_characterized_not_ready`
- case count: `6`
- measured case count: `6`
- timed-out case count: `0`
- resolved correct polarity count: `0`
- clock setting count: `3`
- passing clock setting count: `0`
- uses swapped preamp voltage mapping: `True`
- uses sampled nodes: `False`
- accepted post-layout written: `False`

## First Principle

After polarity is fixed in the latch-alone deck, the latch must still work when its enable time moves. This is a timing question, not a kickback question, because the sampled nodes are still removed.

This run does not pass. All six cases measure and resolve to a strong rail-to-rail difference, but with the opposite sign from the source-paper polarity contract. That means the next circuit question is not coupled kickback yet; it is the exact latch input/output sign convention and clocked deck shape.

## Clock Summary

| clock start ns | measured | resolved | min abs output diff V |
|---:|---:|---:|---:|
| `0.2` | `2` | `0` | `1.370963400e+00` |
| `0.6` | `2` | `0` | `1.370963400e+00` |
| `1.0` | `2` | `0` | `1.370963400e+00` |

## Boundary

does not prove sampled-node kickback, coupled preamp/latch loading, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence
