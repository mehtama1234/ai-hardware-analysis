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
- cycle DAC values V: `[1.343625, 0.7404889, 0.6262081, 0.8089719]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.19493e-08, 7.061794e-08, 6.998092e-08], [6.834213e-08, 1.8, 6.834331e-08, 6.834355e-08], [6.834284e-08, 6.834376e-08, 1.8, 6.834403e-08], [6.833659e-08, 6.834142e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655373, -0.8643535, -0.8652507, -0.8654008, -0.8688458, -0.864778, 0.8637102, -0.8660322, -0.8686744, 0.8643603, -0.8666005, -0.8652633, -0.8687526, 0.8659946, 0.8658216, -0.8666142, -0.8676086, 0.8654638, 0.8668697, 0.8659571]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
