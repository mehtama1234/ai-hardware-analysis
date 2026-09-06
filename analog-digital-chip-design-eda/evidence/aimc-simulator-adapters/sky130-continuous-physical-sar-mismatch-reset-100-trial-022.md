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
- cycle DAC values V: `[1.333351, 0.7408458, 0.6205815, 0.8049867]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.13273e-08, 7.019724e-08, 6.969672e-08], [6.83418e-08, 1.8, 6.834327e-08, 6.834352e-08], [6.834305e-08, 6.834382e-08, 1.8, 6.834407e-08], [6.833677e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865537, -0.8643547, -0.8650843, -0.8653673, -0.8688387, -0.8647562, 0.8638722, -0.8660016, -0.8686621, 0.8643693, -0.8666012, -0.8653403, -0.8687254, 0.866001, 0.8657868, -0.866741, -0.8675169, 0.8654974, 0.8668827, 0.86574]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
