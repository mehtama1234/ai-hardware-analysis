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
- cycle DAC values V: `[1.341588, 0.7403968, 0.6190326, 0.8047843]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.118516e-08, 7.008141e-08, 6.964826e-08], [6.834143e-08, 1.8, 6.834325e-08, 6.834348e-08], [6.83431e-08, 6.834385e-08, 1.8, 6.834408e-08], [6.833671e-08, 6.834145e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655366, -0.8643571, -0.8650834, -0.8654149, -0.868844, -0.8647768, 0.8638878, -0.8659726, -0.8686717, 0.8643776, -0.8665082, -0.8653029, -0.868742, 0.8659861, 0.8658986, -0.8665067, -0.8675269, 0.8654325, 0.8668581, 0.8660506]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
