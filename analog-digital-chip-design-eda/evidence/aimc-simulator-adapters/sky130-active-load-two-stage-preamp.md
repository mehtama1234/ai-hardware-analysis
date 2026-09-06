# Sky130 Active-Load Two-Stage Preamp

- status: `active_load_two_stage_preamp_characterized_not_accepted`
- load bias V: `0.9`
- zero-input offset output V: `0.000212000000000101`
- corrected margin pass: `0` of `2`

This is a matched active-load transistor preamp diagnostic. The offset subtraction is a measured calibration probe, not a statistical offset proof.

| input diff mV | raw output diff V | corrected output diff V | sign pass | margin pass |
|---:|---:|---:|---|---|
| `-0.15297058540778352` | `0.00014999999999987246` | `-6.200000000022854e-05` | `True` | `False` |
| `0.0` | `0.000212000000000101` | `` | `` | `` |
| `0.15297058540778352` | `0.00027200000000005` | `5.999999999994898e-05` | `True` | `False` |

## Refused Claim

does not prove latch behavior, statistical offset, noise, mismatch, DRC/LVS, SAR conversion, or accepted converter evidence
