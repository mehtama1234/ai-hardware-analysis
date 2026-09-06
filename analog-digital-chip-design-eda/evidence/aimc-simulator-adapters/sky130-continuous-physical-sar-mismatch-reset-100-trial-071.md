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
- cycle DAC values V: `[1.342336, 0.7349395, 0.6191851, 0.8007608]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.108553e-08, 7.006909e-08, 6.9588e-08], [6.83411e-08, 1.8, 6.834323e-08, 6.83435e-08], [6.834309e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.8337e-08, 6.834159e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655389, -0.8643326, -0.8650829, -0.8653479, -0.8688408, -0.8646218, 0.8639057, -0.865944, -0.868671, 0.8644496, -0.8665028, -0.8651226, -0.8687492, 0.8659781, 0.8658621, -0.8665314, -0.8676488, 0.8654383, 0.8668751, 0.8659344]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
