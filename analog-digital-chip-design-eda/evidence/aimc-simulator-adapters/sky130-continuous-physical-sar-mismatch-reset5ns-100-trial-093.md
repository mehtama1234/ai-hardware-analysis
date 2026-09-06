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
- cycle DAC values V: `[1.330501, 0.739901, 0.6205751, 0.8053435]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.103237e-08, 7.002213e-08, 6.956558e-08], [6.834148e-08, 1.8, 6.834324e-08, 6.83435e-08], [6.834305e-08, 6.834382e-08, 1.8, 6.834407e-08], [6.833676e-08, 6.834142e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655305, -0.8643501, -0.8650815, -0.8653636, -0.8688332, -0.8647297, 0.8638675, -0.8660066, -0.8686667, 0.8644009, -0.8665957, -0.8653118, -0.8687139, 0.8659897, 0.865806, -0.866729, -0.867445, 0.8654737, 0.8668722, 0.8657598]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
