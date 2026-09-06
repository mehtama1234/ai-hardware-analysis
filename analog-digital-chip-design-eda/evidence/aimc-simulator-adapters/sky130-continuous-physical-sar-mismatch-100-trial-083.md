# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_nominal_map_passed`
- expected code: `2`
- comparator clear flags: `[1, 1, 0, 1]`
- retained logical bits: `[0, 0, 1, 0]`
- final code: `2`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `8` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `20.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `True`
- measured: `True`
- cycle DAC values V: `[1.345406, 0.7411433, 0.6217146, 0.8023253]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.138021e-08, 7.021815e-08, 6.969466e-08], [6.834177e-08, 1.8, 6.834328e-08, 6.834353e-08], [6.834299e-08, 6.834381e-08, 1.8, 6.834407e-08], [6.833698e-08, 6.834156e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655388, -0.8643595, -0.8650878, -0.8653767, -0.8688472, -0.8647931, 0.8638243, -0.8659404, -0.8686757, 0.8643617, -0.8665541, -0.8652047, -0.8687529, 0.8659915, 0.8658638, -0.8664735, -0.8676003, 0.8654491, 0.8668636, 0.8660683]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
