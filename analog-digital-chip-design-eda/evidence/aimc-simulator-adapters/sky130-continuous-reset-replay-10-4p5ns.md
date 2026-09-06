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
- cycle DAC values V: `[1.339079, 0.7382185, 0.6152638, 0.8006046]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.114752e-08, 7.005839e-08, 6.963098e-08], [6.83415e-08, 1.8, 6.834327e-08, 6.83435e-08], [6.834323e-08, 6.83439e-08, 1.8, 6.83441e-08], [6.83369e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655367, -0.8643402, -0.8650723, -0.8653721, -0.868841, -0.8647003, 0.8639842, -0.8659408, -0.8686685, 0.8644108, -0.8664947, -0.8652966, -0.8687458, 0.8660105, 0.8658711, -0.8665971, -0.8675903, 0.8654749, 0.8668689, 0.8658788]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
