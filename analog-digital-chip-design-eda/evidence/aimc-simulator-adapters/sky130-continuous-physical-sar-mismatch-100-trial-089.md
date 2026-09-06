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
- cycle DAC values V: `[1.346408, 0.7391671, 0.6218799, 0.8046622]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.151425e-08, 7.031371e-08, 6.978467e-08], [6.834165e-08, 1.8, 6.834327e-08, 6.834352e-08], [6.834299e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833677e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655392, -0.8643504, -0.8650877, -0.8653973, -0.8688479, -0.8647497, 0.8638215, -0.8659723, -0.8686768, 0.8643853, -0.8665257, -0.8652178, -0.8687562, 0.865986, 0.8658809, -0.8664837, -0.8676257, 0.8654367, 0.8668615, 0.8660583]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
