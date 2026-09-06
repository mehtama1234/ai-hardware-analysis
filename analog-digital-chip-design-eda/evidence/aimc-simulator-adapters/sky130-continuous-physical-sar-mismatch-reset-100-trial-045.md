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
- cycle DAC values V: `[1.33897, 0.7378704, 0.620344, 0.8052392]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.158327e-08, 7.037098e-08, 6.983579e-08], [6.834176e-08, 1.8, 6.834328e-08, 6.834352e-08], [6.834305e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833671e-08, 6.834145e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655381, -0.8643416, -0.8650835, -0.8653746, -0.8688485, -0.8646891, 0.863879, -0.8660049, -0.868668, 0.8644042, -0.8665508, -0.8652952, -0.8687439, 0.8659936, 0.8658202, -0.8666891, -0.867628, 0.8654819, 0.8668803, 0.8657841]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
