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
- cycle DAC values V: `[1.344746, 0.7369815, 0.6227569, 0.8046936]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.107169e-08, 7.006038e-08, 6.958171e-08], [6.834108e-08, 1.8, 6.834321e-08, 6.834349e-08], [6.834296e-08, 6.83438e-08, 1.8, 6.834406e-08], [6.83368e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655385, -0.8643439, -0.8650903, -0.8653843, -0.8688467, -0.8647002, 0.8638009, -0.8659729, -0.8686745, 0.8644225, -0.866512, -0.8651217, -0.86875, 0.865973, 0.8658983, -0.866428, -0.8675746, 0.8653986, 0.866858, 0.8661012]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
