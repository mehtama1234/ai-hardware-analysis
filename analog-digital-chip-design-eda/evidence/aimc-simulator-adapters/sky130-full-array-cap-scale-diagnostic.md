# Sky130 Full-Array Capacitor-Scale Diagnostic

This diagnostic tests whether scaling the complete binary capacitor array restores the compressed upper thresholds.

- topology: `PMOS-only bottom-plate connection to VDD`
- full-array capacitor scale: `8.0x`
- measured codes: `4/4`
- required 4-bit half-LSB: `56.25 mV`
- status: `measured_spacing_pass_but_supply_violation`

## Measurements

| code | DAC top before comparator (V) | correct polarity |
| ---: | ---: | --- |
| 12 | 1.975943 | True |
| 13 | 2.239491 | True |
| 14 | 2.447554 | True |
| 15 | 2.544409 | True |

Adjacent spacings (mV): 263.548, 208.063, 96.855

## Result

Full-array scaling restores monotonic upper-code spacing only by driving the DAC top plate above the 1.8 V supply in this fixture; it is a diagnostic, not an acceptable cell.
The next design must rebalance the charge-transfer network so the required spacing is obtained within the legal supply range.

## Claim Boundary

does not prove converter acceptance, SAR accuracy, PVT/mismatch/noise yield, extracted layout, board behavior, or silicon
