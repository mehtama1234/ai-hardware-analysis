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
- cycle DAC values V: `[1.333213, 0.7442404, 0.6247212, 0.8103858]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.142125e-08, 7.025295e-08, 6.974111e-08], [6.834201e-08, 1.8, 6.834328e-08, 6.834352e-08], [6.834291e-08, 6.834377e-08, 1.8, 6.834404e-08], [6.833653e-08, 6.834132e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655316, -0.8643712, -0.865051, -0.8654131, -0.8688372, -0.8648575, 0.8637479, -0.8660503, -0.8686635, 0.8643205, -0.8666404, -0.8653935, -0.8687198, 0.8660018, 0.8658006, -0.8667132, -0.8674077, 0.8654762, 0.8668711, 0.8658862]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
