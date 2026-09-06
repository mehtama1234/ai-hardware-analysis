# Sky130 Three-Stage Preamp Latch

- status: `three_stage_preamp_latch_open`
- same-run stage-3 offset V: `-0.5688690000000001`
- passing cases: `1` of `2`

This is a bounded third-stage gain experiment, not converter signoff.

| input diff mV | latch output diff V | polarity pass |
|---:|---:|---|
| `-0.15297058540778352` | `-1.79386` | `False` |
| `0.15297058540778352` | `-1.79392` | `True` |

## Refused Claim

does not prove statistical offset, noise, mismatch, DRC/LVS, SAR conversion, or accepted converter evidence
