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
- cycle DAC values V: `[1.340289, 0.7368457, 0.6260347, 0.8104033]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.121552e-08, 7.017895e-08, 6.966944e-08], [6.834114e-08, 1.8, 6.834321e-08, 6.834348e-08], [6.834285e-08, 6.834376e-08, 1.8, 6.834403e-08], [6.83365e-08, 6.834139e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655358, -0.8643419, -0.8650952, -0.8654051, -0.868843, -0.864696, 0.8637165, -0.8660508, -0.8686701, 0.8644218, -0.8665541, -0.8651888, -0.86874, 0.8659742, 0.8658645, -0.8665576, -0.8675154, 0.865404, 0.8668627, 0.8660133]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
