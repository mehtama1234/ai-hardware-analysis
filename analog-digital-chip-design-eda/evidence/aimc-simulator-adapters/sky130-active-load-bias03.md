# Sky130 Active-Load Two-Stage Preamp

- status: `active_load_two_stage_preamp_characterized_not_accepted`
- load bias V: `0.3`
- zero-input offset output V: `2.4000000000024002e-05`
- corrected margin pass: `0` of `2`

This is a matched active-load transistor preamp diagnostic. The offset subtraction is a measured calibration probe, not a statistical offset proof.

| input diff mV | raw output diff V | corrected output diff V | sign pass | margin pass |
|---:|---:|---:|---|---|
| `-0.15297058540778352` | `1.399999999995849e-05` | `-1.0000000000065512e-05` | `True` | `False` |
| `0.0` | `2.4000000000024002e-05` | `` | `` | `` |
| `0.15297058540778352` | `3.2000000000032e-05` | `8.000000000008e-06` | `True` | `False` |

## Refused Claim

does not prove latch behavior, statistical offset, noise, mismatch, DRC/LVS, SAR conversion, or accepted converter evidence
