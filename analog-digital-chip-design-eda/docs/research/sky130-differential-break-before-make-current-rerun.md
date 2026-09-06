# Sky130 Differential Break-Before-Make Current Rerun

The existing transistor-level complementary differential DAC was rerun as the
next candidate after the single-ended continuous path failed endpoint
separability. The current authoritative run used the installed Sky130 ngspice
flow, four-times differential dummy capacitance, a full `1.0` differential
input scale, all 16
physical calibration codes, and the five representative SAR inputs.

The calibration phase measured `16/16` codes and the conversion phase measured
`20/20` physical comparisons. The resulting representative conversions were:

| Expected code | Final code | Correct |
|---:|---:|---|
| 0 | 1 | no |
| 2 | 3 | no |
| 4 | 5 | no |
| 6 | 6 | yes |
| 7 | 7 | yes |

The run therefore achieves `2/5` correct conversions. Its rank-to-logical
mapping aliases physical codes (for example, logical codes 1 and 2 both map
to physical 13), so calibration coverage alone cannot make this a valid
converter. The differential path is retained as the next topology to repair,
but its source common-mode/input-scale and unit-capacitor mapping must be
redesigned before continuous-SAR integration.

Evidence: `evidence/aimc-simulator-adapters/sky130-thermometer-calibrated-physical-sar.json`.
