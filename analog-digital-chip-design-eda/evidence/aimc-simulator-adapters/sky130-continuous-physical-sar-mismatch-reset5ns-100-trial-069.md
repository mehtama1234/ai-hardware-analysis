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
- cycle DAC values V: `[1.334959, 0.7359597, 0.6228962, 0.8064031]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.111881e-08, 7.011604e-08, 6.961392e-08], [6.834124e-08, 1.8, 6.834322e-08, 6.834349e-08], [6.834296e-08, 6.83438e-08, 1.8, 6.834405e-08], [6.833671e-08, 6.834145e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655367, -0.8643336, -0.8650855, -0.8653566, -0.8688388, -0.8646352, 0.863813, -0.8660213, -0.8686713, 0.8644478, -0.8665665, -0.8651934, -0.8687322, 0.8659769, 0.8658216, -0.8666744, -0.8675279, 0.8654438, 0.8668706, 0.8658097]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
