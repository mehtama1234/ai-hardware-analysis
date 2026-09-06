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
- cycle DAC values V: `[1.348237, 0.7351278, 0.6196222, 0.8021938]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.191074e-08, 7.0585e-08, 6.998387e-08], [6.83418e-08, 1.8, 6.83433e-08, 6.834354e-08], [6.834306e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833686e-08, 6.834157e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655479, -0.8643288, -0.8650819, -0.8653619, -0.8688456, -0.8646248, 0.8638969, -0.8659635, -0.868678, 0.864432, -0.8664979, -0.8651864, -0.8687685, 0.8659875, 0.8658545, -0.8665715, -0.8677704, 0.8654704, 0.8668775, 0.8658837]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
