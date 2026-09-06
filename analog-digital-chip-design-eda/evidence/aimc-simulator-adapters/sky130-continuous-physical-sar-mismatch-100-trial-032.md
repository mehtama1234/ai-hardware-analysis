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
- cycle DAC values V: `[1.341647, 0.7413148, 0.6228518, 0.8068797]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.155561e-08, 7.03354e-08, 6.980394e-08], [6.834187e-08, 1.8, 6.834328e-08, 6.834352e-08], [6.834296e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.833666e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655364, -0.8643589, -0.8650892, -0.8654051, -0.8688441, -0.8647961, 0.8637968, -0.8660027, -0.8686722, 0.8643572, -0.8665707, -0.8652978, -0.8687451, 0.8659935, 0.86585, -0.8665804, -0.8675534, 0.8654562, 0.8668657, 0.8659914]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
