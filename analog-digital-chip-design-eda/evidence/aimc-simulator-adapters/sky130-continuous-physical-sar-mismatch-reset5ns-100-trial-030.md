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
- cycle DAC values V: `[1.334843, 0.7388223, 0.6206901, 0.8035143]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.111025e-08, 7.007665e-08, 6.959242e-08], [6.834151e-08, 1.8, 6.834325e-08, 6.834351e-08], [6.834304e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833687e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655369, -0.8643452, -0.8650816, -0.8653513, -0.8688386, -0.8647056, 0.8638654, -0.8659819, -0.8686714, 0.8644117, -0.866577, -0.8652454, -0.8687314, 0.8659873, 0.8658155, -0.866672, -0.8675237, 0.8654694, 0.8668715, 0.8658135]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
