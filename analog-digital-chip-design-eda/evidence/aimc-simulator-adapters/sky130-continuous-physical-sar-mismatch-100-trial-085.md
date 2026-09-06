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
- cycle DAC values V: `[1.340936, 0.7412973, 0.6245967, 0.807767]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.154164e-08, 7.034305e-08, 6.979077e-08], [6.834188e-08, 1.8, 6.834328e-08, 6.834353e-08], [6.83429e-08, 6.834377e-08, 1.8, 6.834404e-08], [6.833665e-08, 6.834142e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655361, -0.8643586, -0.8650921, -0.8653987, -0.8688437, -0.8647956, 0.8637523, -0.8660154, -0.8686714, 0.8643571, -0.8665944, -0.8652777, -0.8687437, 0.8659937, 0.8658321, -0.8666004, -0.8675444, 0.8654573, 0.8668679, 0.8659758]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
