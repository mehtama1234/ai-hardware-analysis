# Sky130 Extracted Frontend Two-Stage Preamp

- status: `two_stage_preamp_offset_corrected_margin_passed_not_layout_or_latch_proof`
- zero-input output offset V: `0.03730330000000004`
- corrected sign pass: `2` of `2`
- corrected margin pass: `2` of `2`

This is a transistor-level two-stage preamp diagnostic. Offset subtraction is a measured diagnostic, not a production calibration proof.

| input diff mV | stage-2 output diff V | corrected output diff V | sign pass | margin pass |
|---:|---:|---:|---|---|
| `-0.15297058540778352` | `0.03519519999999998` | `-0.002108100000000057` | `True` | `True` |
| `0.0` | `0.03730330000000004` | `` | `` | `` |
| `0.15297058540778352` | `0.03935719999999998` | `0.002053899999999942` | `True` | `True` |

## Refused Claim

does not prove calibrated offset statistics, noise, mismatch, latch kickback, DRC/LVS, SAR conversion, or accepted post-layout converter evidence
