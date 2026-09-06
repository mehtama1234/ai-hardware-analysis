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
- cycle DAC values V: `[1.340437, 0.7344414, 0.6249466, 0.8044632]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.130441e-08, 7.026041e-08, 6.967585e-08], [6.834123e-08, 1.8, 6.834322e-08, 6.834351e-08], [6.834288e-08, 6.834378e-08, 1.8, 6.834404e-08], [6.833691e-08, 6.834156e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655336, -0.8643268, -0.865089, -0.865331, -0.8688424, -0.8645976, 0.8637618, -0.8659958, -0.8686766, 0.8644622, -0.8665698, -0.8650567, -0.8687482, 0.8659734, 0.8658149, -0.8666055, -0.8676321, 0.8654379, 0.8668715, 0.8658692]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
