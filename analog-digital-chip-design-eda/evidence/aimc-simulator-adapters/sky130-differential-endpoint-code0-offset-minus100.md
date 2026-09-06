# Sky130 Thermometer Calibrated Physical SAR

- status: `differential_break_before_make_sar_rejected_source_common_mode`
- topology: `complementary_differential_break_before_make_thermometer`
- source acquisition: `4.0 ns`
- calibration codes measured: `16/16`
- physical comparisons: `4/4`
- correct conversions: `0/1`

## Calibration

The thermometer DAC is calibrated at the same source common mode and source-acquisition timing used by the physical comparator trials. Logical SAR trial codes are mapped to the closest measured physical thresholds.

| logical code | physical code | threshold (V) |
| ---: | ---: | ---: |
| 0 | 15 | 1.097484150 |
| 1 | 14 | 0.912327780 |
| 2 | 13 | 0.803977990 |
| 3 | 12 | 0.649165200 |
| 4 | 11 | 0.379168100 |
| 5 | 10 | 0.216172400 |
| 6 | 9 | 0.157874500 |
| 7 | 8 | 0.000000000 |
| 8 | 7 | -0.157874500 |
| 9 | 6 | -0.216172400 |
| 10 | 5 | -0.379168100 |
| 11 | 4 | -0.649165200 |
| 12 | 3 | -0.803977990 |
| 13 | 2 | -0.912327780 |
| 14 | 1 | -1.097484150 |
| 15 | 0 | -1.375138800 |

## Conversions

| expected code | input V | final code | comparisons | correct |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0.056250 | 1 | 4 | False |

## Claim Boundary

does not prove PVT, mismatch/noise yield, continuous multi-cycle SPICE SAR state, extracted layout, area, energy, board behavior, or silicon
