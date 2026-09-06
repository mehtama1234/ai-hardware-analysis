# Sky130 Active-Load Two-Stage Preamp

- status: `active_load_two_stage_preamp_characterized_not_accepted`
- load bias V: `0.7`
- zero-input offset output V: `5.900000000003125e-05`
- corrected margin pass: `0` of `2`

This is a matched active-load transistor preamp diagnostic. The offset subtraction is a measured calibration probe, not a statistical offset proof.

| input diff mV | raw output diff V | corrected output diff V | sign pass | margin pass |
|---:|---:|---:|---|---|
| `-0.15297058540778352` | `3.799999999998249e-05` | `-2.1000000000048757e-05` | `True` | `False` |
| `0.0` | `5.900000000003125e-05` | `` | `` | `` |
| `0.15297058540778352` | `8.000000000008001e-05` | `2.1000000000048757e-05` | `True` | `False` |

## Refused Claim

does not prove latch behavior, statistical offset, noise, mismatch, DRC/LVS, SAR conversion, or accepted converter evidence
