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
- cycle DAC values V: `[1.342746, 0.7358653, 0.6252794, 0.8090756]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.121975e-08, 7.018081e-08, 6.96711e-08], [6.834107e-08, 1.8, 6.834321e-08, 6.834348e-08], [6.834287e-08, 6.834377e-08, 1.8, 6.834404e-08], [6.833655e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655373, -0.8643382, -0.865094, -0.8654015, -0.868845, -0.8646734, 0.8637371, -0.8660328, -0.8686727, 0.8644335, -0.8665293, -0.8651498, -0.8687474, 0.8659706, 0.8658815, -0.8665063, -0.8675532, 0.8653948, 0.8668604, 0.8660487]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
