# Sky130 Bottom-Plate Cell

- status: `bottom_plate_cell_characterized`
- measured cases: `4` of `4`
- break-before-make interval: `0.020000000000000018 ns`
- low-side pulse width: `0.18 ns`

This isolated fixture tests the bottom-plate switch before it is placed back into the binary array. The low-side device is released first; the high-side device is enabled only after the non-overlap interval. The top plate and bottom plate are measured before and after the transition.

| input V | target rail | bottom before V | bottom after V | expected V | bottom error V |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0.300 | vdd | 0.000273 | 1.222389 | 1.800 | -0.577611 |
| 0.900 | vdd | 0.000273 | 1.222389 | 1.800 | -0.577611 |
| 1.500 | vdd | 0.000273 | 1.222389 | 1.800 | -0.577611 |
| 0.900 | ground | 0.000088 | 0.000007 | 0.000 | 0.000007 |

## Refused Claim

does not prove the four-bit DAC, SAR accuracy, mismatch/noise yield, PVT behavior, extracted layout, board behavior, or silicon
