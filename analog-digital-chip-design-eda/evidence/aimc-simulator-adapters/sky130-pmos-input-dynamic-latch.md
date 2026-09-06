# Sky130 PMOS-Input Dynamic Latch

- status: `pmos_input_dynamic_latch_open`
- same-run preamp trim V: `-0.01885300000000001`
- passing cases: `1` of `2`

This is a different regenerative architecture: outputs precharge low and a PMOS input pair pulls the winning side high during evaluation.

| input diff mV | latch output diff V | polarity pass |
|---:|---:|---|
| `-0.15297058540778352` | `1.77863` | `False` |
| `0.15297058540778352` | `1.7789` | `True` |

## Refused Claim

does not prove noise, statistical offset, mismatch, sampled-node kickback, DRC/LVS, SAR conversion, or accepted converter evidence
