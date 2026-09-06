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
- cycle DAC values V: `[1.346887, 0.7380709, 0.6274662, 0.8075636]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.178101e-08, 7.054181e-08, 6.989091e-08], [6.834175e-08, 1.8, 6.834327e-08, 6.834354e-08], [6.834279e-08, 6.834374e-08, 1.8, 6.834403e-08], [6.833671e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655393, -0.8643444, -0.8650966, -0.8653768, -0.8688484, -0.8647245, 0.8636766, -0.8660138, -0.8686776, 0.8643943, -0.8665847, -0.8651334, -0.8687604, 0.8659851, 0.8658342, -0.8665312, -0.8676519, 0.8654379, 0.8668679, 0.8660211]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
