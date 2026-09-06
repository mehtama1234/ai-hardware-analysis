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
- cycle DAC values V: `[1.343012, 0.7366691, 0.6287948, 0.8086838]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.131666e-08, 7.026834e-08, 6.968136e-08], [6.834121e-08, 1.8, 6.83432e-08, 6.83435e-08], [6.834275e-08, 6.834373e-08, 1.8, 6.834402e-08], [6.833669e-08, 6.834148e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655368, -0.8643412, -0.8650998, -0.8653703, -0.8688455, -0.8646919, 0.8636398, -0.8660291, -0.868673, 0.864422, -0.8665892, -0.8650698, -0.8687478, 0.8659746, 0.8658376, -0.8665193, -0.8675655, 0.865406, 0.8668663, 0.866039]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
