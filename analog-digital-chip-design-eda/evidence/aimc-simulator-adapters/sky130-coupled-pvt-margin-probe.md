# Sky130 Coupled PVT Margin Probe

- status: `slow_cold_low_supply_margin_boundary_characterized`
- corner: `ss`, `-20 C`, `1.62 V`
- physical code: `6`
- measured: `7` of `7`
- correct polarity: `3` of `7`

| reference V | DAC-reference margin V | output difference V | correct polarity |
| ---: | ---: | ---: | --- |
| 0.500 | 0.138817 | -1.438379 | True |
| 0.550 | 0.088841 | -1.432171 | True |
| 0.580 | 0.058878 | -1.427716 | True |
| 0.604 | 0.034886 | 1.426722 | False |
| 0.620 | 0.018848 | 1.426961 | False |
| 0.650 | -0.011155 | -1.427019 | False |
| 0.700 | -0.061139 | -1.426875 | False |

The low-supply corner requires a measured comparator-margin guard; nominal sign evidence cannot be extrapolated through the approximately 35 mV transition region.

## Refused Claim

does not prove a full PVT SAR, offset/noise yield, continuous SAR, extracted layout, board behavior, or silicon
