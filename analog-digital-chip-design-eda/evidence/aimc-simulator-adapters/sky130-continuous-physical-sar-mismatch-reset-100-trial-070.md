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
- cycle DAC values V: `[1.349659, 0.7314926, 0.6201833, 0.8017246]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.150315e-08, 7.035994e-08, 6.9801e-08], [6.834118e-08, 1.8, 6.834325e-08, 6.834351e-08], [6.834304e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833691e-08, 6.834161e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655483, -0.864317, -0.8650838, -0.8653517, -0.868847, -0.864536, 0.8638847, -0.8659573, -0.8686788, 0.8644811, -0.866458, -0.8650526, -0.8687699, 0.8659656, 0.8658841, -0.8664816, -0.8677741, 0.8654264, 0.8668732, 0.8659601]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
