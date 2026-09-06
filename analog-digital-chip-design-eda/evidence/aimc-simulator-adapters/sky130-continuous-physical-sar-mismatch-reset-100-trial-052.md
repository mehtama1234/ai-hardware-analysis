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
- cycle DAC values V: `[1.343387, 0.7355596, 0.622026, 0.8019727]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.137729e-08, 7.027213e-08, 6.970841e-08], [6.834144e-08, 1.8, 6.834325e-08, 6.834353e-08], [6.834298e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833693e-08, 6.834154e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655391, -0.8643333, -0.865087, -0.8653386, -0.8688413, -0.8646358, 0.8638399, -0.8659612, -0.8686724, 0.8644363, -0.8665436, -0.8651079, -0.8687527, 0.8659839, 0.8658261, -0.866574, -0.8676801, 0.8654557, 0.8668793, 0.8658941]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
