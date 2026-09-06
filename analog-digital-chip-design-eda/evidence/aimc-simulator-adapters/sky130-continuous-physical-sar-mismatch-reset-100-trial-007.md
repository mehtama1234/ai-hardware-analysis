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
- cycle DAC values V: `[1.336906, 0.7377076, 0.6161733, 0.8004134]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.084661e-08, 6.988472e-08, 6.948378e-08], [6.834111e-08, 1.8, 6.834322e-08, 6.834348e-08], [6.83432e-08, 6.834388e-08, 1.8, 6.83441e-08], [6.833696e-08, 6.834154e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655376, -0.8643449, -0.8650782, -0.8653614, -0.8688469, -0.8646865, 0.8639695, -0.8659384, -0.8686653, 0.864421, -0.8665058, -0.8652472, -0.8687321, 0.8659848, 0.865866, -0.8665794, -0.8675416, 0.8654512, 0.8668742, 0.8659029]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
