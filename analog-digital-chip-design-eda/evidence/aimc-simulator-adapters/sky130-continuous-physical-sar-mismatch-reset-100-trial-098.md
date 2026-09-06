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
- cycle DAC values V: `[1.344358, 0.7342675, 0.6181122, 0.8011058]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.12397e-08, 7.01597e-08, 6.96744e-08], [6.83412e-08, 1.8, 6.834325e-08, 6.83435e-08], [6.834312e-08, 6.834387e-08, 1.8, 6.834409e-08], [6.833692e-08, 6.834158e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655393, -0.864329, -0.8650807, -0.8653586, -0.8688419, -0.8646053, 0.8639299, -0.8659483, -0.8686731, 0.8644543, -0.8664748, -0.8651506, -0.8687568, 0.8659776, 0.8658787, -0.8665252, -0.8676857, 0.8654388, 0.8668734, 0.8659347]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
