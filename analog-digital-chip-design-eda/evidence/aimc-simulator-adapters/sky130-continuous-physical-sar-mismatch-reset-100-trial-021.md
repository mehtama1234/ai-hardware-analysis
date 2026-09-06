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
- cycle DAC values V: `[1.341754, 0.7379839, 0.6204314, 0.8021666]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.156745e-08, 7.036123e-08, 6.979947e-08], [6.834176e-08, 1.8, 6.834328e-08, 6.834353e-08], [6.834304e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833693e-08, 6.834155e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655387, -0.8643421, -0.8650839, -0.8653509, -0.868846, -0.8646916, 0.8638769, -0.8659634, -0.868671, 0.8644031, -0.8665541, -0.8652197, -0.8687516, 0.8659937, 0.865818, -0.866628, -0.8676639, 0.8654807, 0.8668804, 0.8658443]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
