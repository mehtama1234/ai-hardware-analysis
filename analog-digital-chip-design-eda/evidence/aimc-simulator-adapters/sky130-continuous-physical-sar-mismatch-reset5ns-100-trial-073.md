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
- cycle DAC values V: `[1.338753, 0.7368433, 0.6205922, 0.8022147]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.116114e-08, 7.011852e-08, 6.961505e-08], [6.834137e-08, 1.8, 6.834324e-08, 6.834351e-08], [6.834304e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833695e-08, 6.834155e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655349, -0.8643372, -0.8650815, -0.8653457, -0.8688401, -0.8646562, 0.8638683, -0.8659643, -0.8686751, 0.8644357, -0.8665464, -0.8651691, -0.8687424, 0.8659805, 0.865836, -0.8666048, -0.8675955, 0.8654534, 0.8668693, 0.8658732]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
