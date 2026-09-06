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
- cycle DAC values V: `[1.351441, 0.73513, 0.6167513, 0.7982113]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.174652e-08, 7.045352e-08, 6.989584e-08], [6.834172e-08, 1.8, 6.834331e-08, 6.834354e-08], [6.834316e-08, 6.834388e-08, 1.8, 6.83441e-08], [6.833709e-08, 6.834166e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655483, -0.8643291, -0.8650774, -0.8653531, -0.8688489, -0.8646248, 0.8639596, -0.865908, -0.8686812, 0.8644333, -0.8664587, -0.8651544, -0.8687753, 0.8659864, 0.8658828, -0.8664824, -0.8678076, 0.8654667, 0.8668741, 0.8659563]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
