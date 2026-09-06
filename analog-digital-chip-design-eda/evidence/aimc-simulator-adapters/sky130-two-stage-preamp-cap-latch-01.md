# Sky130 Two-Stage Preamp Capacitive Latch

- status: `two_stage_preamp_capacitive_latch_open`
- coupling capacitance fF: `0.1`
- passing cases: `1` of `2`

This test inserts capacitive isolation between the preamp outputs and latch gates so the latch has no DC loading path into the preamp.

| input diff mV | gate differential after V | gate transition V | latch output diff V | polarity pass |
|---:|---:|---:|---:|---|
| `-0.15297058540778352` | `-0.23418260000000002` | `0.2346838000000001` | `-1.37227` | `True` |
| `0.15297058540778352` | `-0.23550459999999995` | `0.23604309999999995` | `-1.37227` | `False` |

## Refused Claim

does not prove noise, statistical offset, mismatch, sampled-node kickback, DRC/LVS, SAR conversion, or accepted converter evidence
