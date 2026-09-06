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
- cycle DAC values V: `[1.344017, 0.737371, 0.6192528, 0.8004313]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.149551e-08, 7.030926e-08, 6.976462e-08], [6.834173e-08, 1.8, 6.834329e-08, 6.834354e-08], [6.834308e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833703e-08, 6.83416e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655391, -0.8643395, -0.865082, -0.8653494, -0.8688418, -0.8646775, 0.863904, -0.8659394, -0.8686734, 0.864411, -0.8665292, -0.8651903, -0.8687577, 0.8659914, 0.8658365, -0.8665782, -0.8676929, 0.8654755, 0.8668787, 0.8658883]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
