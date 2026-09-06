# Sky130 Active-Load Two-Stage Preamp

- status: `active_load_two_stage_preamp_characterized_not_accepted`
- load bias V: `0.5`
- zero-input offset output V: `3.2999999999949736e-05`
- corrected margin pass: `0` of `2`

This is a matched active-load transistor preamp diagnostic. The offset subtraction is a measured calibration probe, not a statistical offset proof.

| input diff mV | raw output diff V | corrected output diff V | sign pass | margin pass |
|---:|---:|---:|---|---|
| `-0.15297058540778352` | `2.1000000000048757e-05` | `-1.1999999999900979e-05` | `True` | `False` |
| `0.0` | `3.2999999999949736e-05` | `` | `` | `` |
| `0.15297058540778352` | `4.599999999999049e-05` | `1.3000000000040757e-05` | `True` | `False` |

## Refused Claim

does not prove latch behavior, statistical offset, noise, mismatch, DRC/LVS, SAR conversion, or accepted converter evidence
