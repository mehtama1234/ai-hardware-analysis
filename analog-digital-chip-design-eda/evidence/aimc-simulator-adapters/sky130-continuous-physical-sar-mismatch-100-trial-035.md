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
- cycle DAC values V: `[1.348195, 0.7369426, 0.6246608, 0.8097927]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.193242e-08, 7.061487e-08, 7.001913e-08], [6.834184e-08, 1.8, 6.834329e-08, 6.834353e-08], [6.834289e-08, 6.834378e-08, 1.8, 6.834404e-08], [6.833646e-08, 6.834141e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655398, -0.864339, -0.8650913, -0.8654198, -0.8688494, -0.8646987, 0.8637533, -0.8660425, -0.8686791, 0.8644035, -0.8665252, -0.8652453, -0.868765, 0.8659839, 0.8658728, -0.8665563, -0.8676899, 0.865438, 0.8668635, 0.8659963]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
