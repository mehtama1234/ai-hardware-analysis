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
- cycle DAC values V: `[1.345619, 0.736997, 0.6176956, 0.8016605]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.084005e-08, 6.987868e-08, 6.948721e-08], [6.834092e-08, 1.8, 6.834322e-08, 6.834346e-08], [6.834314e-08, 6.834387e-08, 1.8, 6.834409e-08], [6.833687e-08, 6.834154e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655392, -0.8643455, -0.8650821, -0.8654001, -0.868847, -0.8647012, 0.8639186, -0.8659292, -0.8686752, 0.8644272, -0.8664431, -0.8651641, -0.8687498, 0.8659699, 0.865946, -0.8663491, -0.8675693, 0.8653878, 0.8668495, 0.8661498]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
