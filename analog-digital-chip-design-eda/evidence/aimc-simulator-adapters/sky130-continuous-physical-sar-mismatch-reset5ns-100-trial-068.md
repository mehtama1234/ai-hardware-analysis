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
- cycle DAC values V: `[1.348066, 0.7349346, 0.6193163, 0.8018582]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.188613e-08, 7.056953e-08, 6.997255e-08], [6.834188e-08, 1.8, 6.834331e-08, 6.834355e-08], [6.834307e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833687e-08, 6.834157e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655413, -0.864326, -0.8650802, -0.8653595, -0.8688499, -0.8646097, 0.8639042, -0.8659589, -0.868683, 0.864445, -0.8664881, -0.8651756, -0.8687681, 0.8659816, 0.8658655, -0.8665616, -0.8677639, 0.8654646, 0.8668673, 0.865892]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
