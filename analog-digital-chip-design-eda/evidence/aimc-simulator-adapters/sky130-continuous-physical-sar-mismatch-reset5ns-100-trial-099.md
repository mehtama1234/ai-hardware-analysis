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
- cycle DAC values V: `[1.3437, 0.7309066, 0.6184568, 0.8031856]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.104635e-08, 7.006211e-08, 6.961068e-08], [6.834087e-08, 1.8, 6.834322e-08, 6.834348e-08], [6.834311e-08, 6.834386e-08, 1.8, 6.834408e-08], [6.833676e-08, 6.834154e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655368, -0.8643145, -0.8650805, -0.8653679, -0.8688456, -0.8645066, 0.8639236, -0.8659768, -0.8686789, 0.8645051, -0.8664306, -0.8650995, -0.8687532, 0.8659579, 0.8659045, -0.8664995, -0.8676702, 0.8653985, 0.8668595, 0.8659556]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
