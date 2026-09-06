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
- cycle DAC values V: `[1.341189, 0.7384458, 0.6220763, 0.8042322]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.181027e-08, 7.052504e-08, 6.991426e-08], [6.834206e-08, 1.8, 6.834331e-08, 6.834355e-08], [6.834299e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833682e-08, 6.834151e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865538, -0.8643425, -0.8651758, -0.8653572, -0.868847, -0.864702, 0.8638384, -0.8659918, -0.8686707, 0.8643931, -0.8665797, -0.8652493, -0.8687498, 0.8659977, 0.8657949, -0.8666819, -0.8676688, 0.8654943, 0.8668827, 0.8657877]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
