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
- cycle DAC values V: `[1.340346, 0.7369413, 0.6198147, 0.8029506]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.135158e-08, 7.022829e-08, 6.971593e-08], [6.834152e-08, 1.8, 6.834326e-08, 6.834351e-08], [6.834306e-08, 6.834384e-08, 1.8, 6.834407e-08], [6.833685e-08, 6.834152e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655379, -0.8643389, -0.8650832, -0.8653594, -0.8688484, -0.8646681, 0.8638912, -0.8659739, -0.8686692, 0.8644201, -0.8665336, -0.8652227, -0.8687438, 0.8659881, 0.8658355, -0.8666217, -0.8676351, 0.8654656, 0.8668784, 0.8658533]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
