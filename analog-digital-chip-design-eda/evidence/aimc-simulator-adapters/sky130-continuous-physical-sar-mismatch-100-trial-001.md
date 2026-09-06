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
- cycle DAC values V: `[1.341515, 0.7383837, 0.623512, 0.8086439]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.136588e-08, 7.024227e-08, 6.973887e-08], [6.834137e-08, 1.8, 6.834324e-08, 6.834349e-08], [6.834294e-08, 6.834379e-08, 1.8, 6.834405e-08], [6.833655e-08, 6.834141e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655364, -0.8643476, -0.8650907, -0.865411, -0.868844, -0.8647314, 0.8637817, -0.8660265, -0.8686717, 0.8643998, -0.8665395, -0.8652497, -0.8687438, 0.8659812, 0.8658737, -0.8665528, -0.8675414, 0.8654226, 0.866862, 0.8660143]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
