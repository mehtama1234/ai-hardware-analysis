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
- cycle DAC values V: `[1.341633, 0.7342881, 0.6199472, 0.8059376]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.149789e-08, 7.033702e-08, 6.9823e-08], [6.834127e-08, 1.8, 6.834325e-08, 6.834349e-08], [6.834306e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833663e-08, 6.834146e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655386, -0.8643282, -0.8650831, -0.8653832, -0.8688458, -0.8646058, 0.8638892, -0.8660141, -0.8686705, 0.86445, -0.8664969, -0.8652367, -0.8687468, 0.8659803, 0.8658602, -0.866631, -0.867664, 0.8654483, 0.866876, 0.8658389]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
