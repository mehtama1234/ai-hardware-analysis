# Sky130 PMOS Gate Overdrive Diagnostic

- topology: `PMOS-only bottom-plate connection to VDD`
- PMOS gate low level: `-0.600 V`
- measured codes: `2` of `2`
- code 14 to 15 spacing: `17.118 mV`
- required 4-bit half-LSB: `56.25 mV`

## Result

Driving the selected PMOS gate below ground is a headroom diagnostic. It does not materially increase the upper threshold spacing: the measured spacing remains far below the half-LSB requirement. The collapse is therefore not repaired by gate overdrive alone; the charge-transfer topology or controlled bottom-plate waveform must change.

## Claim Boundary

does not prove converter acceptance, full SAR accuracy, PVT/mismatch yield, extracted layout, board behavior, or silicon

## Measurements

| code | DAC top after redistribution (V) | comparator polarity |
| ---: | ---: | --- |
| 14 | 2.389895 | True |
| 15 | 2.407013 | True |
