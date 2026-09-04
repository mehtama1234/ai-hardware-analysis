# Sky130 Bottom-Plate Cell

- status: `bottom_plate_cell_incomplete`
- measured cases: `0` of `4`
- break-before-make interval: `0.18 ns`

This isolated fixture tests the bottom-plate switch before it is placed back into the binary array. The low-side device is released first; the high-side device is enabled only after the non-overlap interval. The top plate and bottom plate are measured before and after the transition.

| input V | target rail | bottom before V | bottom after V | expected V | bottom error V |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0.300 | vdd | timeout | timeout | - | timeout |
| 0.900 | vdd | timeout | timeout | - | timeout |
| 1.500 | vdd | timeout | timeout | - | timeout |
| 0.900 | ground | timeout | timeout | - | timeout |

## Refused Claim

does not prove the four-bit DAC, SAR accuracy, mismatch/noise yield, PVT behavior, extracted layout, board behavior, or silicon
