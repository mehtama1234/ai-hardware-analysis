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
- cycle DAC values V: `[1.34132, 0.7390687, 0.6244279, 0.806448]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.116892e-08, 7.012342e-08, 6.961857e-08], [6.83413e-08, 1.8, 6.834322e-08, 6.83435e-08], [6.83429e-08, 6.834378e-08, 1.8, 6.834405e-08], [6.833674e-08, 6.834147e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655365, -0.8643516, -0.8650928, -0.8653846, -0.8688437, -0.8647469, 0.8637575, -0.8659974, -0.8686713, 0.8643948, -0.866565, -0.86518, -0.8687419, 0.8659815, 0.8658587, -0.8665177, -0.8675243, 0.8654211, 0.8668635, 0.8660434]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
