# Sky130 Bottom-Plate Cell

- status: `bottom_plate_cell_measured_not_accepted`
- measured cases: `1` of `1`
- break-before-make interval: `0.020000000000000018 ns`
- low-side pulse width: `0.18 ns`

- high-side device bank: `1` parallel device(s)

This isolated fixture tests the bottom-plate switch before it is placed back into the binary array. The low-side device is released first; the high-side device is enabled only after the non-overlap interval. The top plate and bottom plate are measured before and after the transition.

| input V | target rail | bottom before V | bottom after V | expected V | bottom error V |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0.900 | vdd | 0.000001 | 0.472123 | 1.800 | -1.327877 |

## Refused Claim

does not prove the four-bit DAC, SAR accuracy, mismatch/noise yield, PVT behavior, extracted layout, board behavior, or silicon
