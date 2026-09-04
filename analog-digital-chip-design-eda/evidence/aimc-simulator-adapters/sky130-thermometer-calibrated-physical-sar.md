# Sky130 Thermometer Calibrated Physical SAR

- status: `differential_break_before_make_sar_rejected_source_common_mode`
- topology: `complementary_differential_break_before_make_thermometer`
- source acquisition: `2.59 ns`
- calibration codes measured: `16/16`
- physical comparisons: `20/20`
- correct conversions: `2/5`

## Calibration

The thermometer DAC is calibrated at the same source common mode and source-acquisition timing used by the physical comparator trials. Logical SAR trial codes are mapped to the closest measured physical thresholds.

| logical code | physical code | threshold (V) |
| ---: | ---: | ---: |
| 0 | 13 | 0.531271500 |
| 1 | 13 | 0.531271500 |
| 2 | 12 | 0.398641600 |
| 3 | 12 | 0.398641600 |
| 4 | 11 | 0.276021200 |
| 5 | 11 | 0.276021200 |
| 6 | 10 | 0.171115300 |
| 7 | 9 | 0.083527300 |
| 8 | 8 | 0.000000000 |
| 9 | 7 | -0.083527300 |
| 10 | 6 | -0.171115300 |
| 11 | 5 | -0.276021200 |
| 12 | 5 | -0.276021200 |
| 13 | 4 | -0.398641600 |
| 14 | 4 | -0.398641600 |
| 15 | 3 | -0.531271500 |

## Conversions

| expected code | input V | final code | comparisons | correct |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0.056250 | 1 | 4 | False |
| 2 | 0.281250 | 3 | 4 | False |
| 4 | 0.506250 | 5 | 4 | False |
| 6 | 0.731250 | 6 | 4 | True |
| 7 | 0.843750 | 7 | 4 | True |

## Claim Boundary

does not prove PVT, mismatch/noise yield, continuous multi-cycle SPICE SAR state, extracted layout, area, energy, board behavior, or silicon
