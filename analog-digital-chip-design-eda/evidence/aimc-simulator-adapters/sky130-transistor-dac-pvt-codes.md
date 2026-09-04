# Sky130 Transistor DAC Representative PVT Codes

- status: `representative_dac_pvt_measured_not_full_calibration_proof`
- corners: `3`
- codes per corner: `3`
- measured cases: `8` of `9`
- timed-out cases: `1`
- half-LSB passes: `2` of `8`

## First-Principles Reading

A calibration table is only useful if the code-to-voltage curve is repeatable as operating conditions move. This targeted run checks the endpoints and midscale at the nominal, slow/cold/low-supply, and fast/hot/high-supply corners. It is intentionally smaller than a full all-code PVT matrix, but it tests whether the calibration assumption is already visibly unstable.

## Refused Claim

does not prove all-code calibration stability, mismatch/noise yield, SAR accuracy, extracted layout, board behavior, or silicon
