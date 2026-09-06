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
- cycle DAC values V: `[1.340327, 0.7386081, 0.6222981, 0.8075316]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.111034e-08, 7.007207e-08, 6.961787e-08], [6.834122e-08, 1.8, 6.834322e-08, 6.834348e-08], [6.834298e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.83366e-08, 6.834142e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655359, -0.8643498, -0.8650891, -0.8654105, -0.8688431, -0.8647366, 0.8638117, -0.866011, -0.8686702, 0.8644019, -0.8665287, -0.8652476, -0.8687387, 0.8659793, 0.8658846, -0.8665293, -0.8675063, 0.8654149, 0.8668599, 0.8660357]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
