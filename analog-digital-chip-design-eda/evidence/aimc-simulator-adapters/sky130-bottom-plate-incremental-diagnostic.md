# Sky130 Bottom-Plate Incremental Diagnostic

- status: `incremental_diagnostic_isolated_timeout`
- measured stages: `4` of `5`

The stages start from the known-good transmission-gate sample-switch deck and add one bottom-plate element at a time.

| stage | measured | sampled V | bottom V | sample error V |
| --- | --- | ---: | ---: | ---:|
| baseline | True | 0.900137 | n/a | 1.369000e-04 |
| baseline_plus_capacitor | True | 0.900137 | -0.06019909 | 1.371000e-04 |
| plus_capacitor_plus_nfet | True | 0.342206 | 0.03895692 | 5.577937e-01 |
| large_sample_switch_plus_nfet | True | 0.865989 | 0.0131484 | 3.401060e-02 |
| very_large_sample_switch_plus_nfet | False | timeout | timeout | timeout |

## Refused Claim

does not prove a working bottom-plate cell, four-bit DAC, SAR accuracy, PVT behavior, mismatch/noise yield, extracted layout, board behavior, or silicon
