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
- cycle DAC values V: `[1.346419, 0.7394165, 0.6228265, 0.8044005]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.150936e-08, 7.031789e-08, 6.977086e-08], [6.834168e-08, 1.8, 6.834327e-08, 6.834352e-08], [6.834295e-08, 6.83438e-08, 1.8, 6.834406e-08], [6.833682e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655392, -0.8643515, -0.8650894, -0.8653857, -0.868848, -0.8647552, 0.8637981, -0.8659692, -0.8686768, 0.8643821, -0.8665427, -0.8651935, -0.8687563, 0.8659869, 0.8658691, -0.8664842, -0.867626, 0.8654394, 0.866863, 0.8660582]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
