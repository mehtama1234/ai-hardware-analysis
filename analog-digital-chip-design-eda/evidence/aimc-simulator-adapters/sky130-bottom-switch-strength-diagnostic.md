# Sky130 Bottom-Switch Strength Diagnostic

This sweep tests whether stronger PMOS bottom-plate charge transfer restores the compressed upper DAC thresholds.

- topology: `PMOS-only bottom-plate connection to VDD`
- scales: `[2.0, 4.0]` relative to the 16 um PMOS / 8 um NMOS baseline
- required 4-bit half-LSB: `56.25 mV`

## Result

larger PMOS bottom-plate switches do not restore high-code threshold spacing; charge-transfer topology or waveform must change

| switch scale | code 14 top (V) | code 15 top (V) | spacing (mV) | both measured |
| ---: | ---: | ---: | ---: | --- |
| 2.0x | 2.386335 | 2.403600 | 17.265 | True |
| 4.0x | 2.381243 | 2.398493 | 17.250 | True |

## Claim Boundary

does not prove converter acceptance, full SAR accuracy, PVT/mismatch yield, extracted layout, board behavior, or silicon
