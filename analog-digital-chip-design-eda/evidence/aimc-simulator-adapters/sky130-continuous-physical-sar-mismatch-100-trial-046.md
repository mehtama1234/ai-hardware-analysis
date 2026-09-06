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
- cycle DAC values V: `[1.331569, 0.7461379, 0.6217921, 0.8067744]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.107603e-08, 7.000806e-08, 6.9567e-08], [6.834189e-08, 1.8, 6.834327e-08, 6.834351e-08], [6.834301e-08, 6.83438e-08, 1.8, 6.834406e-08], [6.833671e-08, 6.834137e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655308, -0.8643815, -0.8650882, -0.8654048, -0.868836, -0.8648969, 0.8638204, -0.8660008, -0.8686613, 0.8643012, -0.866632, -0.8654046, -0.8687104, 0.8660042, 0.8658141, -0.8666719, -0.867351, 0.8654781, 0.8668691, 0.8659321]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
