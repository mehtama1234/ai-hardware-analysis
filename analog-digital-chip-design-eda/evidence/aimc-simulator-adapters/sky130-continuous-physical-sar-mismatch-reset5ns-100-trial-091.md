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
- cycle DAC values V: `[1.342002, 0.7377231, 0.6191252, 0.8008828]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.14136e-08, 7.02568e-08, 6.972971e-08], [6.834175e-08, 1.8, 6.834328e-08, 6.834353e-08], [6.834309e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833699e-08, 6.834157e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655353, -0.8643392, -0.8650784, -0.8653505, -0.8688441, -0.8646798, 0.8639069, -0.8659457, -0.8686783, 0.8644186, -0.8665336, -0.8652066, -0.868752, 0.865987, 0.8658414, -0.8665963, -0.8676621, 0.8654728, 0.8668694, 0.8658738]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
