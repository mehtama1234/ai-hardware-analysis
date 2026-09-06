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
- cycle DAC values V: `[1.334776, 0.7431732, 0.6189257, 0.8021077]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.145797e-08, 7.024861e-08, 6.973586e-08], [6.834228e-08, 1.8, 6.834333e-08, 6.834356e-08], [6.834311e-08, 6.834384e-08, 1.8, 6.834408e-08], [6.833693e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655374, -0.8643632, -0.8650813, -0.8653589, -0.8688445, -0.8648057, 0.8639094, -0.8659622, -0.8686639, 0.8643367, -0.8666097, -0.8653677, -0.8687305, 0.86601, 0.8657799, -0.8667288, -0.8675432, 0.8655209, 0.8668836, 0.8657514]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
