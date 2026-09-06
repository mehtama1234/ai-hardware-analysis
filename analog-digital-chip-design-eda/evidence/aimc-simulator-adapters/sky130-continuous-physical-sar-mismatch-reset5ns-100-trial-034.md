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
- cycle DAC values V: `[1.336378, 0.7374705, 0.6217103, 0.8046227]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.120585e-08, 7.015198e-08, 6.964385e-08], [6.834152e-08, 1.8, 6.834325e-08, 6.834351e-08], [6.8343e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.83368e-08, 6.834148e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655351, -0.8643391, -0.8649145, -0.8653517, -0.8688375, -0.8646741, 0.8638418, -0.8659971, -0.868673, 0.8644266, -0.8665695, -0.8652202, -0.8687366, 0.8659837, 0.8658184, -0.8666684, -0.8675569, 0.8654623, 0.8668714, 0.865813]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
