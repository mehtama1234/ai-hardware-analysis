# Sky130 Continuous Physical SAR

- status: `continuous_physical_sar_candidate_measured_not_accepted`
- expected code: `2`
- comparator clear flags: `[0, 0, 0, 0]`
- retained logical bits: `[1, 1, 1, 1]`
- final code: `15`
- continuous PMOS/NMOS switch width um: `8.0` / `64.0`
- continuous PMOS bank: `8` parallel device(s)
- bottom diode clamp: `False` (area `1.0`)
- dead-time clamp: `False` (width `1.0` um)
- conversion ground precharge: `False` (2.0 ns)
- top dummy capacitor: `0.5p`
- transient step ps: `100.0`
- conversions measured/required: `5`/`5`
- conversion coverage complete: `True`
- all conversions correct: `False`
- measured: `True`
- cycle DAC values V: `[0.02994413, -0.7447001, -0.6871621, -0.6596406]`
- cycle DAC legal range: `False`
- gate legal range: `True`
- bottom-plate legal range: `False`
- bottom-plate debug values V: `[[1.8, 1.8, 1.8, 1.800004], [0.0474518, 1.805096, 1.803504, 1.802657], [0.0159664, 0.004877474, 1.802511, 1.801866], [0.001568175, 0.003445779, 0.00223725, 1.801338]]`
- comparator differences V: `[-0.8607408, -0.8622915, -0.862395, -0.8607633, 0.8632219, 0.8628821, 0.8635327, 0.8641557, -0.8685457, -0.8719157, -0.8833519, -0.8904687, 0.8672462, 0.8668451, 0.8673693, 0.8678861, -0.8680592, -0.8719106, -0.8854673, -0.8961894]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient; fixed-decision diagnostic when enabled; not closed-loop qualification, PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
