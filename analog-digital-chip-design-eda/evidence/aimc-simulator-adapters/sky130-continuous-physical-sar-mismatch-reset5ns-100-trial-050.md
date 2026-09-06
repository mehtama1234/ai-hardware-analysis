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
- cycle DAC values V: `[1.346095, 0.7331907, 0.6173304, 0.8018412]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.142812e-08, 7.027747e-08, 6.978146e-08], [6.834131e-08, 1.8, 6.834327e-08, 6.83435e-08], [6.834315e-08, 6.834388e-08, 1.8, 6.834409e-08], [6.833682e-08, 6.834155e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655405, -0.8643211, -0.865078, -0.8653705, -0.868848, -0.8645661, 0.863948, -0.8659582, -0.8686812, 0.864473, -0.8664417, -0.8651669, -0.8687614, 0.8659704, 0.8658987, -0.8665208, -0.8677197, 0.8654331, 0.8668619, 0.8659323]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
