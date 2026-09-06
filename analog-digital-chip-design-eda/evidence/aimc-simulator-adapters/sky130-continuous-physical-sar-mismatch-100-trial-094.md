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
- cycle DAC values V: `[1.339422, 0.7455096, 0.6222512, 0.8043278]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.153473e-08, 7.029133e-08, 6.975661e-08], [6.834245e-08, 1.8, 6.834334e-08, 6.834357e-08], [6.834299e-08, 6.83438e-08, 1.8, 6.834406e-08], [6.833686e-08, 6.834146e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655343, -0.8643766, -0.8650882, -0.8653869, -0.8688423, -0.8648846, 0.8638093, -0.8659681, -0.86867, 0.8642969, -0.866623, -0.8653452, -0.8687281, 0.8660077, 0.8658126, -0.866615, -0.8675147, 0.8654934, 0.8668704, 0.8659667]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
