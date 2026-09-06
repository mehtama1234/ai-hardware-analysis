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
- cycle DAC values V: `[1.33236, 0.744819, 0.6167461, 0.799704]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.114139e-08, 7.003093e-08, 6.958173e-08], [6.834211e-08, 1.8, 6.834331e-08, 6.834354e-08], [6.834318e-08, 6.834387e-08, 1.8, 6.834409e-08], [6.833707e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865537, -0.8643717, -0.8650782, -0.8653535, -0.8688373, -0.8648377, 0.8639557, -0.8659288, -0.8686636, 0.8643205, -0.8666086, -0.8653869, -0.86872, 0.8660122, 0.8657869, -0.86671, -0.8674824, 0.8655229, 0.8668827, 0.8657803]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
