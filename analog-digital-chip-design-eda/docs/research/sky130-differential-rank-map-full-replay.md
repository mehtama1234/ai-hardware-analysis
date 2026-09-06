# Sky130 Differential Rank-Map Full Replay

The 1× differential dummy candidate was rerun with the injective reverse-rank
map and a calibrated `+60 mV` source offset. Calibration was reused from the
complete 1× artifact; all five representative conversions were then replayed
with four physical comparisons each.

| Expected code | Final code | Correct |
|---:|---:|---|
| 0 | 2 | no |
| 2 | 3 | no |
| 4 | 4 | yes |
| 6 | 5 | no |
| 7 | 7 | yes |

All `20/20` comparisons measured, giving `2/5` correct conversions. The high
endpoint now passes, but the low and middle boundaries still use the wrong
physical trial behavior. This confirms that a rank map plus one global offset
is not enough; the physical transfer is input-dependent and needs a signed
per-boundary characterization or a redesigned DAC mapping.

The artifact records the rank-map mode, offset, and calibration source:
`evidence/aimc-simulator-adapters/sky130-thermometer-calibrated-physical-sar.json`.
It remains diagnostic evidence, not converter acceptance.
