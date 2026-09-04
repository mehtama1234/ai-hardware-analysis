# Sky130 LSB Ratio Diagnostic

This run changes the LSB capacitor while keeping the PMOS-only switch topology and timing fixed.

- LSB capacitor scale: `4.0x`
- measured codes: `4` of `4`
- adjacent spacings mV: `[293.782, -104.561, 144.058]`
- monotonic: `False`
- required half-LSB: `56.25 mV`

## Result

isolated LSB enlargement changes the transfer non-monotonically; the capacitor network must be rebalanced as a complete topology

| code | DAC top after redistribution (V) | comparator polarity |
| ---: | ---: | --- |
| 12 | 2.091050 | True |
| 13 | 2.384832 | True |
| 14 | 2.280271 | True |
| 15 | 2.424329 | True |

## Claim Boundary

does not prove converter acceptance, full SAR accuracy, PVT/mismatch yield, extracted layout, board behavior, or silicon
