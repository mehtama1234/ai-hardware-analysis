# Sky130 Capacitor-Scale Common-Mode Diagnostic

This diagnostic tests whether lowering the sampled common-mode makes the otherwise promising full-array capacitor ratio legal.

- topology: `PMOS-only bottom-plate connection to VDD`
- full-array capacitor scale: `8.0x`
- sampled input common-mode: `0.000 V`
- measured codes: `4/4`
- status: `candidate_common_mode_rebalance`

## Measurements

| code | DAC top before comparator (V) | correct polarity |
| ---: | ---: | --- |
| 12 | 1.075629 | True |
| 13 | 1.346174 | True |
| 14 | 1.597136 | True |
| 15 | 1.799298 | True |

Adjacent spacings (mV): 270.545, 250.962, 202.162

## Result

At zero sampled common-mode, the 8x array reaches the spacing target while the measured upper-code top-plate values remain within the 1.8 V supply in this fixture. This is a candidate operating-point change, not converter acceptance.
The next run must extend this candidate to all codes and PVT, then test settling, mismatch, noise, and retained-bit SAR behavior before it can replace the blocked converter boundary.

## Claim Boundary

does not prove all-code SAR accuracy, PVT/mismatch/noise yield, extracted layout, energy, board behavior, or silicon
