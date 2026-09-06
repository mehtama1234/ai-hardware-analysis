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
- cycle DAC values V: `[1.337696, 0.7390369, 0.6192721, 0.8034809]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.139083e-08, 7.023529e-08, 6.973321e-08], [6.834172e-08, 1.8, 6.834328e-08, 6.834352e-08], [6.834309e-08, 6.834384e-08, 1.8, 6.834408e-08], [6.833681e-08, 6.834148e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655381, -0.8643469, -0.8650821, -0.8653675, -0.8688476, -0.8647159, 0.8639029, -0.8659809, -0.8686668, 0.864393, -0.8665559, -0.8652984, -0.8687388, 0.8659957, 0.8658199, -0.8666749, -0.8675952, 0.8654849, 0.8668799, 0.8658037]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
