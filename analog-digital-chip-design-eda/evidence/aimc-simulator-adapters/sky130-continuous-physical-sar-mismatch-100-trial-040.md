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
- cycle DAC values V: `[1.346915, 0.7329485, 0.6209982, 0.8061407]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.096886e-08, 7.000371e-08, 6.957423e-08], [6.834074e-08, 1.8, 6.83432e-08, 6.834346e-08], [6.834301e-08, 6.834383e-08, 1.8, 6.834406e-08], [6.833662e-08, 6.834148e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655399, -0.8643281, -0.8650875, -0.8654109, -0.8688484, -0.8646045, 0.8638457, -0.8659916, -0.8686765, 0.8644716, -0.8664277, -0.8651007, -0.8687539, 0.8659568, 0.8659517, -0.866364, -0.8676003, 0.8653581, 0.8668485, 0.8661379]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
