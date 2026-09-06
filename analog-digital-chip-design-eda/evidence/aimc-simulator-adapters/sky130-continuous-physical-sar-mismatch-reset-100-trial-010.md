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
- cycle DAC values V: `[1.339203, 0.7383558, 0.6154815, 0.8008415]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.117065e-08, 7.007254e-08, 6.96416e-08], [6.834146e-08, 1.8, 6.834327e-08, 6.83435e-08], [6.834322e-08, 6.834389e-08, 1.8, 6.83441e-08], [6.833689e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865538, -0.8643454, -0.8650762, -0.8653745, -0.8688485, -0.8647007, 0.863984, -0.865944, -0.8686678, 0.8644052, -0.8664993, -0.8653034, -0.8687412, 0.865991, 0.8658659, -0.8666037, -0.867597, 0.8654707, 0.866875, 0.8658734]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
