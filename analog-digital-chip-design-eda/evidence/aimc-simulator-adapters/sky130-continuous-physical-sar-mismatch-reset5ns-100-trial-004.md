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
- cycle DAC values V: `[1.334554, 0.7398141, 0.6217474, 0.8045215]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.134684e-08, 7.022687e-08, 6.969693e-08], [6.834177e-08, 1.8, 6.834327e-08, 6.834353e-08], [6.834301e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833683e-08, 6.834147e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655384, -0.8643481, -0.865083, -0.8653526, -0.8688387, -0.8647278, 0.8638403, -0.8659958, -0.8686714, 0.8643949, -0.8666053, -0.8652744, -0.8687322, 0.8659927, 0.8657937, -0.8667133, -0.8675311, 0.8654858, 0.8668739, 0.8657681]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
