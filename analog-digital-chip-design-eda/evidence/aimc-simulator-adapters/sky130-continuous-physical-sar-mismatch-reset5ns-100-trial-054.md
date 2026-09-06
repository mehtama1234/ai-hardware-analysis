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
- cycle DAC values V: `[1.341467, 0.7340996, 0.6196477, 0.8056084]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.14629e-08, 7.03149e-08, 6.980659e-08], [6.834137e-08, 1.8, 6.834326e-08, 6.83435e-08], [6.834307e-08, 6.834385e-08, 1.8, 6.834407e-08], [6.833664e-08, 6.834147e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655345, -0.8643243, -0.8650793, -0.8653806, -0.8688435, -0.8645887, 0.8638964, -0.8660097, -0.8686775, 0.8644624, -0.8664875, -0.8652265, -0.8687514, 0.8659742, 0.8658709, -0.8666215, -0.8676603, 0.8654423, 0.8668658, 0.8658475]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
