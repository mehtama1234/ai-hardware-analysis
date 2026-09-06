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
- cycle DAC values V: `[1.338964, 0.736151, 0.6196604, 0.8043968]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.132113e-08, 7.021415e-08, 6.971821e-08], [6.834139e-08, 1.8, 6.834325e-08, 6.83435e-08], [6.834307e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833674e-08, 6.834148e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655355, -0.8643333, -0.8650795, -0.8653692, -0.8688401, -0.8646395, 0.8638903, -0.8659935, -0.8686753, 0.8644408, -0.8665203, -0.8652385, -0.8687441, 0.86598, 0.8658517, -0.866637, -0.867609, 0.8654543, 0.8668678, 0.8658386]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
