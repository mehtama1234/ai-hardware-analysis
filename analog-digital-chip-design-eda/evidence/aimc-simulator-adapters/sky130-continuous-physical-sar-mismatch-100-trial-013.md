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
- cycle DAC values V: `[1.34682, 0.7375668, 0.6215527, 0.805322]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.143479e-08, 7.027164e-08, 6.976381e-08], [6.834141e-08, 1.8, 6.834325e-08, 6.83435e-08], [6.8343e-08, 6.834382e-08, 1.8, 6.834406e-08], [6.83367e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655395, -0.8643441, -0.8650873, -0.8654042, -0.8688483, -0.8647137, 0.8638302, -0.8659811, -0.8686771, 0.8644075, -0.8664985, -0.8652009, -0.868757, 0.8659794, 0.8658997, -0.8664607, -0.8676277, 0.8654191, 0.8668584, 0.8660739]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
