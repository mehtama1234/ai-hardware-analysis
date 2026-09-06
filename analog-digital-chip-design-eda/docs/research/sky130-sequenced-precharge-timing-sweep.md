# Sky130 Sequenced-Precharge Timing Sweep

The phase-separated candidate grounds the bottom plates during acquisition,
opens them for non-overlap, and then performs decision-dependent
redistribution. The precharge duration was swept around the 4.0 ns source
acquisition boundary while keeping the tuned reference profile fixed at
`0.3, 0.3, 0.3, 0.7, 0.72 V`.

| Bottom precharge | Conversion result | DAC thresholds legal | Bottom plates legal |
|---:|---|---|---|
| 3.5 ns | `0→2, 2→2, 4→4, 6→6, 7→6` | yes | no |
| 4.0 ns | `0→4, 2→2, 4→4, 6→6, 7→6` | yes | no |
| 4.5 ns | `0→2, 2→2, 4→5, 6→6, 7→6` | yes | no |

The middle conversions remain stable across the timing window, but the
endpoints do not become separable and the strict 0–1.8 V bottom-plate gate
still fails. The timing change is therefore not sufficient to close the
converter.

This is the boundary for the single-ended phase-control approach. Further
precharge-duration tuning is not promoted; the next design should alter the
MSB/common-mode charge-transfer topology, using the existing differential
break-before-make candidate as the next physical implementation path.

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-sequenced-precharge-pre35-full.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-sequenced-precharge-full.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-sequenced-precharge-pre45-full.json`
