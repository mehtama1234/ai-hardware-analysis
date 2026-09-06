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
- cycle DAC values V: `[1.344567, 0.7399557, 0.6229852, 0.8051665]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.147299e-08, 7.029381e-08, 6.975652e-08], [6.834169e-08, 1.8, 6.834327e-08, 6.834352e-08], [6.834295e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.833678e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655377, -0.8643538, -0.8650897, -0.8653891, -0.8688464, -0.864767, 0.863794, -0.8659796, -0.8686749, 0.864376, -0.8665534, -0.8652195, -0.8687524, 0.8659883, 0.8658625, -0.8665127, -0.8675951, 0.8654421, 0.8668638, 0.8660403]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
