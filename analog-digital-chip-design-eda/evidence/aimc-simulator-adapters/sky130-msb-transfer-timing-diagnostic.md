# Sky130 MSB Transfer Timing Diagnostic

This diagnostic tests whether the code `7 -> 8` failure in the 8x,
zero-common-mode candidate is caused only by insufficient redistribution time.

| redistribution interval | code 7 top (V) | code 8 top (V) | spacing (mV) | polarity |
| ---: | ---: | ---: | ---: | --- |
| 5 ns | 1.183938 | 0.328446 | -855.492 | both correct |
| 20 ns | 0.153749 | 0.059172 | -94.577 | both correct |

## Result

Longer PMOS bottom-plate redistribution does not restore the MSB transition.
The timing-only repair is rejected. The next candidate must change the MSB
charge-transfer topology or use explicit precharge/split-capacitor control.

## Claim Boundary

This is a two-code nominal transient diagnostic. It does not prove converter
acceptance, SAR accuracy, PVT/mismatch/noise yield, extracted layout, energy,
board behavior, or silicon.
