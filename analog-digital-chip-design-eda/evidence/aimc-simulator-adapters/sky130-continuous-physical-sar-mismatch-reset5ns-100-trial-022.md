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
- cycle DAC values V: `[1.333188, 0.7406603, 0.6202908, 0.8046662]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.130276e-08, 7.0182e-08, 6.968559e-08], [6.834188e-08, 1.8, 6.834328e-08, 6.834353e-08], [6.834306e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833678e-08, 6.834144e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655387, -0.8643516, -0.8650804, -0.8653642, -0.8688378, -0.8647455, 0.8638743, -0.8659973, -0.8686699, 0.8643841, -0.8665978, -0.8653309, -0.8687276, 0.8659952, 0.8658005, -0.8667318, -0.8675072, 0.8654921, 0.8668733, 0.8657493]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
