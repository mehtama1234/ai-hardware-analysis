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
- cycle DAC values V: `[1.330852, 0.7422166, 0.6212532, 0.8065246]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.140175e-08, 7.024085e-08, 6.973225e-08], [6.834208e-08, 1.8, 6.83433e-08, 6.834354e-08], [6.834303e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.83367e-08, 6.834139e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655362, -0.8643599, -0.8651363, -0.8653741, -0.8688347, -0.8647857, 0.8638562, -0.8660224, -0.8686583, 0.8643516, -0.8666286, -0.8653922, -0.8687186, 0.8660064, 0.8657645, -0.8667981, -0.8674809, 0.8655111, 0.8668846, 0.8656754]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
