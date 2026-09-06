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
- cycle DAC values V: `[1.340278, 0.7443997, 0.620625, 0.8042255]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.143121e-08, 7.022055e-08, 6.972774e-08], [6.834222e-08, 1.8, 6.834332e-08, 6.834355e-08], [6.834304e-08, 6.834382e-08, 1.8, 6.834407e-08], [6.833681e-08, 6.834145e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655357, -0.8643724, -0.8650854, -0.8654007, -0.8688429, -0.8648619, 0.8638492, -0.865966, -0.8686708, 0.864315, -0.8665853, -0.8653537, -0.8687406, 0.8660032, 0.8658418, -0.8665872, -0.8675247, 0.865481, 0.8668668, 0.8659888]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
