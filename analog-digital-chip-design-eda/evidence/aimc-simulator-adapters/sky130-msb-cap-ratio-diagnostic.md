# Sky130 MSB Capacitor-Ratio Diagnostic

This sweep tests whether the code `7 -> 8` reversal is caused by the MSB
capacitor ratio in the 8x, zero-common-mode candidate.

| MSB capacitor scale | code 7 top (V) | code 8 top (V) | spacing (mV) |
| ---: | ---: | ---: | ---: |
| 0.125x | 1.503584 | 0.233889 | -1269.695 |
| 0.25x | 1.270614 | 0.296476 | -974.138 |
| 0.5x | 1.204039 | 0.318186 | -885.853 |
| 1.0x | 1.183938 | 0.328446 | -855.492 |
| 2.0x | 1.174803 | 0.333568 | -841.235 |

## Result

MSB capacitor ratio alone does not restore monotonicity. Comparator polarity
remains correct, so the failure is in the physical MSB charge-transfer path.
The next candidate needs explicit MSB precharge/isolation or a different DAC
architecture.

## Claim Boundary

This is a nominal two-code diagnostic. It does not prove converter acceptance,
SAR accuracy, PVT/mismatch/noise yield, extracted layout, energy, board
behavior, or silicon.
