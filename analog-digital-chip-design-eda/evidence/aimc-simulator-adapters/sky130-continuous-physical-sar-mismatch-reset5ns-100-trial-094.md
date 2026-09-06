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
- cycle DAC values V: `[1.336877, 0.7432987, 0.6184629, 0.8000771]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.152733e-08, 7.028681e-08, 6.975333e-08], [6.834253e-08, 1.8, 6.834335e-08, 6.834358e-08], [6.834312e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833708e-08, 6.834155e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655353, -0.8643614, -0.8650791, -0.8653484, -0.8688379, -0.8648057, 0.8639201, -0.8659345, -0.868674, 0.8643377, -0.8666071, -0.865333, -0.868739, 0.8660032, 0.8657923, -0.8666921, -0.8675826, 0.8655223, 0.8668746, 0.8657873]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
