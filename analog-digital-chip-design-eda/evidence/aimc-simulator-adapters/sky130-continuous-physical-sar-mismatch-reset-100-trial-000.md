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
- cycle DAC values V: `[1.337822, 0.7378885, 0.6200996, 0.8011742]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.099972e-08, 7.000714e-08, 6.953257e-08], [6.834129e-08, 1.8, 6.834323e-08, 6.83435e-08], [6.834306e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833703e-08, 6.834157e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655376, -0.8643446, -0.8652768, -0.8653441, -0.868848, -0.8646903, 0.8638838, -0.8659499, -0.8686664, 0.8644149, -0.8665572, -0.8651792, -0.8687365, 0.866008, 0.8658239, -0.866602, -0.8675674, 0.8654606, 0.866879, 0.8658803]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
