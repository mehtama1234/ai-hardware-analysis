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
- cycle DAC values V: `[1.352276, 0.7275503, 0.6156034, 0.7970535]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.087653e-08, 6.995067e-08, 6.951908e-08], [6.834066e-08, 1.8, 6.834323e-08, 6.834349e-08], [6.83432e-08, 6.83439e-08, 1.8, 6.83441e-08], [6.833714e-08, 6.834173e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655436, -0.8643031, -0.8650728, -0.8653455, -0.8688531, -0.8644152, 0.8639852, -0.8658919, -0.8686851, 0.864542, -0.8663468, -0.8649079, -0.8687716, 0.8659429, 0.8659594, -0.866276, -0.8677724, 0.865363, 0.8668507, 0.8660999]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
