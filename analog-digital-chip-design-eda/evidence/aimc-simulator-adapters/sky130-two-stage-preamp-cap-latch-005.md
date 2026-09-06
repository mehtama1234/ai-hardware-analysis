# Sky130 Two-Stage Preamp Capacitive Latch

- status: `two_stage_preamp_capacitive_latch_open`
- coupling capacitance fF: `0.05`
- passing cases: `1` of `2`

This test inserts capacitive isolation between the preamp outputs and latch gates so the latch has no DC loading path into the preamp.

| input diff mV | gate differential after V | gate transition V | latch output diff V | polarity pass |
|---:|---:|---:|---:|---|
| `-0.15297058540778352` | `-0.24020609999999998` | `0.24046040000000002` | `-1.3723` | `True` |
| `0.15297058540778352` | `-0.24012100000000003` | `0.240394` | `-1.3723` | `False` |

## Refused Claim

does not prove noise, statistical offset, mismatch, sampled-node kickback, DRC/LVS, SAR conversion, or accepted converter evidence
