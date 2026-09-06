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
- cycle DAC values V: `[1.34343, 0.7382356, 0.6214937, 0.8060785]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.121915e-08, 7.013436e-08, 6.966584e-08], [6.834129e-08, 1.8, 6.834324e-08, 6.834349e-08], [6.8343e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.833666e-08, 6.834145e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655376, -0.8643478, -0.8650875, -0.8654076, -0.8688454, -0.8647286, 0.8638314, -0.8659912, -0.8686735, 0.8644036, -0.8665102, -0.8652283, -0.8687478, 0.8659795, 0.8658951, -0.8664901, -0.8675656, 0.8654168, 0.8668586, 0.8660593]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
