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
- cycle DAC values V: `[1.344196, 0.7397763, 0.6222974, 0.8053527]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.143444e-08, 7.026497e-08, 6.974679e-08], [6.834162e-08, 1.8, 6.834326e-08, 6.834351e-08], [6.834298e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833674e-08, 6.834148e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655379, -0.8643532, -0.8650886, -0.8653979, -0.8688462, -0.8647631, 0.8638109, -0.8659818, -0.8686745, 0.8643796, -0.8665417, -0.8652352, -0.868751, 0.8659871, 0.8658713, -0.8665117, -0.8675867, 0.8654387, 0.8668627, 0.8660416]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
