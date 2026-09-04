# Sky130 Thermometer DAC Comparator

- status: `thermometer_candidate_rejected`
- topology: `complementary differential 16-unit charge-transfer DAC`
- unit capacitor: `1.000e-12 F`
- bottom switch scale: `1.0`
- source acquisition: `2.59 ns`
- per-code timeout: `30.0 s`
- codes measured: `0/2`
- minimum spacing (mV): `None`
- required half-LSB (mV): `56.25`
- full-scale target (V): `1.6875`
- full-scale coverage: `False`
- maximum top plate (V): `None`

| code | DAC top (V) | correct polarity |
| ---: | ---: | --- |
| 0 | incomplete | False |
| 15 | incomplete | False |

## Result

The candidate is accepted only if all requested codes converge with full-scale coverage, monotonic half-LSB spacing, legal node range, and correct comparator polarity. It remains a larger-area converter candidate until SAR, PVT, mismatch, noise, settling, extraction, and energy gates pass.

## Claim Boundary

does not prove SAR accuracy, PVT/mismatch/noise yield, extracted layout, area, energy, board behavior, silicon, or model replacement readiness
