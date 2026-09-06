# Sky130 Extracted Frontend Two-Stage Preamp

- status: `two_stage_preamp_characterized_not_accepted`
- zero-input output offset V: `0.0`
- corrected sign pass: `2` of `2`
- corrected margin pass: `0` of `2`

This is a transistor-level two-stage preamp diagnostic. Offset subtraction is a measured diagnostic, not a production calibration proof.

| input diff mV | stage-2 output diff V | corrected output diff V | sign pass | margin pass |
|---:|---:|---:|---|---|
| `-0.15297058540778352` | `-2.9999999999752447e-06` | `-2.9999999999752447e-06` | `True` | `False` |
| `0.0` | `0.0` | `` | `` | `` |
| `0.15297058540778352` | `3.999999999892978e-06` | `3.999999999892978e-06` | `True` | `False` |

## Refused Claim

does not prove calibrated offset statistics, noise, mismatch, latch kickback, DRC/LVS, SAR conversion, or accepted post-layout converter evidence
