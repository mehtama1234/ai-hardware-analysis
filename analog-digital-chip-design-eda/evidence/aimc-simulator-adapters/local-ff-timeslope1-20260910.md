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
- cycle DAC values V: `[1.294067, 0.7025447, 0.5902155, 0.8050973]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.799991, 2.445163e-06, 2.350283e-06, 2.331723e-06], [2.521441e-06, 1.799992, 1.77571e-06, 1.770877e-06], [1.871752e-06, 2.31144e-06, 1.799992, 1.757636e-06], [1.971164e-06, 1.811937e-06, 1.799995, 1.799992]]`
- comparator differences V: `[-0.7323969, -0.7307203, -0.7307607, -0.731088, -0.7348828, -0.7315373, 0.7307055, -0.7326635, -0.7355418, 0.731388, -0.7330659, -0.7326997, -0.7357965, 0.7322149, 0.7330561, -0.7343905, -0.7349712, 0.7317399, 0.7334576, 0.7335397]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
