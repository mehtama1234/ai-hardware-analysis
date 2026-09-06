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
- cycle DAC values V: `[1.337202, 0.7404819, 0.6272796, 0.8092286]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.123052e-08, 7.017826e-08, 6.964053e-08], [6.834145e-08, 1.8, 6.834322e-08, 6.83435e-08], [6.834281e-08, 6.834374e-08, 1.8, 6.834403e-08], [6.833664e-08, 6.834141e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865534, -0.864357, -0.8650972, -0.8653833, -0.8688406, -0.8647774, 0.8636805, -0.8660358, -0.8686672, 0.8643759, -0.8666242, -0.8652141, -0.8687309, 0.865987, 0.8658143, -0.8666112, -0.8674626, 0.865436, 0.8668691, 0.8659753]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
