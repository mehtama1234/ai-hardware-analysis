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
- cycle DAC values V: `[1.336541, 0.7376557, 0.6220027, 0.8049445]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.127853e-08, 7.019791e-08, 6.967687e-08], [6.834145e-08, 1.8, 6.834324e-08, 6.834351e-08], [6.834299e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833679e-08, 6.834148e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655374, -0.8643425, -0.865087, -0.8653561, -0.8688463, -0.8646848, 0.8638396, -0.8660015, -0.8686617, 0.8644134, -0.8665759, -0.8652303, -0.8687351, 0.8659896, 0.8658053, -0.8666776, -0.8675649, 0.8654681, 0.866881, 0.8658043]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
