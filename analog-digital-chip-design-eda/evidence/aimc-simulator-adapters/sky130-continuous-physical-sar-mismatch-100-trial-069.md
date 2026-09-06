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
- cycle DAC values V: `[1.337513, 0.7381836, 0.6267122, 0.81059]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.113843e-08, 7.012857e-08, 6.96229e-08], [6.834116e-08, 1.8, 6.83432e-08, 6.834348e-08], [6.834283e-08, 6.834375e-08, 1.8, 6.834403e-08], [6.833652e-08, 6.834138e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655333, -0.8643478, -0.8650965, -0.8653991, -0.8688408, -0.8647264, 0.8636974, -0.8660535, -0.8686674, 0.8644078, -0.8665845, -0.8652034, -0.8687311, 0.8659777, 0.865845, -0.8665892, -0.8674624, 0.8654112, 0.8668651, 0.8659932]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
