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
- cycle DAC values V: `[1.342384, 0.7381748, 0.6236834, 0.8054168]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.106086e-08, 7.005482e-08, 6.957007e-08], [6.834115e-08, 1.8, 6.834321e-08, 6.834349e-08], [6.834293e-08, 6.834379e-08, 1.8, 6.834405e-08], [6.833679e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655372, -0.8643487, -0.8650918, -0.8653818, -0.8688449, -0.8647271, 0.8637769, -0.8659831, -0.8686722, 0.8644085, -0.8665429, -0.8651454, -0.8687437, 0.865977, 0.8658755, -0.8664724, -0.8675332, 0.8654083, 0.866861, 0.8660749]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
