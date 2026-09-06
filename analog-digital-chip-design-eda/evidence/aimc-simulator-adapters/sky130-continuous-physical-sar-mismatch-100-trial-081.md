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
- cycle DAC values V: `[1.340942, 0.741245, 0.6234922, 0.8090126]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.167169e-08, 7.041297e-08, 6.987304e-08], [6.8342e-08, 1.8, 6.83433e-08, 6.834353e-08], [6.834294e-08, 6.834379e-08, 1.8, 6.834405e-08], [6.833654e-08, 6.834138e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655354, -0.8643575, -0.8650899, -0.8654174, -0.8688436, -0.8647944, 0.863781, -0.8660316, -0.8686714, 0.8643548, -0.8665764, -0.8653379, -0.8687447, 0.865995, 0.8658434, -0.8666264, -0.8675542, 0.8654622, 0.8668669, 0.8659516]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
