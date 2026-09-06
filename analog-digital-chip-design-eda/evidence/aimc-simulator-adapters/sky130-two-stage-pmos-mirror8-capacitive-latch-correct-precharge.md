# Sky130 Two-Stage Preamp Capacitive Latch

- status: `two_stage_preamp_capacitive_latch_open`
- coupling capacitance fF: `0.2`
- passing cases: `1` of `2`

This test inserts capacitive isolation between the preamp outputs and latch gates so the latch has no DC loading path into the preamp.

| input diff mV | gate differential after V | gate transition V | latch output diff V | polarity pass |
|---:|---:|---:|---:|---|
| `-0.15297058540778352` | `-0.39039019999999997` | `0.3957852` | `-1.79886` | `True` |
| `0.15297058540778352` | `0.41763340000000004` | `0.4190954000000001` | `-1.79886` | `False` |

## Refused Claim

does not prove noise, statistical offset, mismatch, sampled-node kickback, DRC/LVS, SAR conversion, or accepted converter evidence
