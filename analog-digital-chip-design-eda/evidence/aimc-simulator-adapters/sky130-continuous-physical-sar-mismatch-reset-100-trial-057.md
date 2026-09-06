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
- cycle DAC values V: `[1.33585, 0.7375548, 0.6175278, 0.8022178]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.091623e-08, 6.993813e-08, 6.952021e-08], [6.834114e-08, 1.8, 6.834322e-08, 6.834348e-08], [6.834315e-08, 6.834387e-08, 1.8, 6.834409e-08], [6.833686e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655378, -0.864344, -0.8650803, -0.8653661, -0.8688454, -0.8646831, 0.863941, -0.8659634, -0.8686642, 0.8644218, -0.8665215, -0.8652568, -0.8687297, 0.8659851, 0.8658538, -0.8666153, -0.8675306, 0.8654525, 0.8668757, 0.8658703]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
