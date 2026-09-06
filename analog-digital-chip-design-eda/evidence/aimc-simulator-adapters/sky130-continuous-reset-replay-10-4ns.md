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
- cycle DAC values V: `[1.339133, 0.7382804, 0.6153607, 0.8007113]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.111559e-08, 7.003886e-08, 6.961632e-08], [6.834148e-08, 1.8, 6.834327e-08, 6.83435e-08], [6.834322e-08, 6.83439e-08, 1.8, 6.83441e-08], [6.83369e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655336, -0.8643483, -0.8650722, -0.8653733, -0.8688398, -0.8646917, 0.8639772, -0.8659423, -0.8686771, 0.8644082, -0.8665042, -0.8652997, -0.8687503, 0.8659833, 0.865869, -0.8666002, -0.8675921, 0.8654672, 0.8668664, 0.8658761]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
