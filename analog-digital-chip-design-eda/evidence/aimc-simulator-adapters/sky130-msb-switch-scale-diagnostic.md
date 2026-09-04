# Sky130 MSB Switch-Scale Diagnostic

| selected MSB PMOS scale | code 7 | code 8 | spacing (mV) |
| ---: | --- | ---: | ---: |
| 2x | timeout | 0.621947 | incomplete |
| 4x | 1.183938 | 0.959683 | -224.255 |

## Result

Scaling only the selected MSB PMOS does not restore code 7 to 8 monotonicity.
Switch sizing alone is rejected; the cell needs a different MSB charge-transfer
topology.

## Claim Boundary

This is a nominal two-code diagnostic. It does not prove converter acceptance,
SAR accuracy, PVT/mismatch/noise yield, extracted layout, energy, board
behavior, or silicon.
