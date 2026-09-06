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
- cycle DAC values V: `[1.344184, 0.7340714, 0.6178041, 0.8007687]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.121347e-08, 7.014325e-08, 6.966235e-08], [6.834122e-08, 1.8, 6.834325e-08, 6.83435e-08], [6.834313e-08, 6.834387e-08, 1.8, 6.834409e-08], [6.833693e-08, 6.834158e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655362, -0.864326, -0.8650791, -0.8653555, -0.8688461, -0.8645887, 0.8639372, -0.8659437, -0.8686799, 0.8644667, -0.8664652, -0.8651398, -0.8687552, 0.865985, 0.8658892, -0.866515, -0.867683, 0.8654325, 0.8668631, 0.8659423]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
