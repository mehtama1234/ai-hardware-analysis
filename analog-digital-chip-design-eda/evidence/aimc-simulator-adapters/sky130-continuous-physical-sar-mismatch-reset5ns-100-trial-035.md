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
- cycle DAC values V: `[1.34565, 0.7346931, 0.6207519, 0.8054751]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.203392e-08, 7.067912e-08, 7.006653e-08], [6.83419e-08, 1.8, 6.834331e-08, 6.834354e-08], [6.834303e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833665e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655365, -0.8643243, -0.8650801, -0.8653767, -0.8688478, -0.8646036, 0.8638666, -0.8660082, -0.8686761, 0.8644463, -0.8665031, -0.8652291, -0.8687636, 0.8659818, 0.8658538, -0.866634, -0.8677379, 0.8654667, 0.8668688, 0.8658247]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
