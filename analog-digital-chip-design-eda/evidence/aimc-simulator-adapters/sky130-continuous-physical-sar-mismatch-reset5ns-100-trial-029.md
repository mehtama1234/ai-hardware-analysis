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
- cycle DAC values V: `[1.339809, 0.7359467, 0.6198349, 0.8011768]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.10543e-08, 7.005069e-08, 6.956711e-08], [6.834116e-08, 1.8, 6.834322e-08, 6.83435e-08], [6.834306e-08, 6.834384e-08, 1.8, 6.834408e-08], [6.8337e-08, 6.834158e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655337, -0.8643342, -0.8650805, -0.8653423, -0.8688415, -0.864635, 0.8638859, -0.8659499, -0.8686759, 0.8644484, -0.8665247, -0.8651353, -0.8687442, 0.8659761, 0.8658523, -0.8665635, -0.8676044, 0.8654414, 0.8668672, 0.8659103]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
