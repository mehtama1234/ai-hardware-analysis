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
- cycle DAC values V: `[1.3388, 0.7378481, 0.6249526, 0.8097723]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.111899e-08, 7.01035e-08, 6.962247e-08], [6.834114e-08, 1.8, 6.834321e-08, 6.834347e-08], [6.834289e-08, 6.834377e-08, 1.8, 6.834404e-08], [6.833652e-08, 6.834139e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655342, -0.8643465, -0.8650936, -0.8654071, -0.8688419, -0.864719, 0.8637447, -0.866042, -0.8686686, 0.8644118, -0.866555, -0.8652192, -0.8687346, 0.8659765, 0.8658661, -0.8665635, -0.8674832, 0.8654084, 0.8668624, 0.8660118]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
