# Sky130 Bottom-Plate Cell

- status: `bottom_plate_cell_characterized`
- measured cases: `4` of `4`
- break-before-make interval: `0.12 ns`
- low-side pulse width: `0.18 ns`

- high-side device bank: `1` parallel device(s)

This isolated fixture tests the bottom-plate switch before it is placed back into the binary array. The low-side device is released first; the high-side device is enabled only after the non-overlap interval. The top plate and bottom plate are measured before and after the transition.

| input V | target rail | bottom before V | bottom after V | expected V | bottom error V |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0.300 | vdd | 0.119011 | 0.293199 | 1.800 | -1.506801 |
| 0.900 | vdd | 0.119011 | 0.293199 | 1.800 | -1.506801 |
| 1.500 | vdd | 0.119011 | 0.293199 | 1.800 | -1.506801 |
| 0.900 | ground | 0.000004 | 0.000000 | 0.000 | 0.000000 |

## Refused Claim

does not prove the four-bit DAC, SAR accuracy, mismatch/noise yield, PVT behavior, extracted layout, board behavior, or silicon
