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
- cycle DAC values V: `[1.341083, 0.7382609, 0.6223662, 0.8047058]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.189576e-08, 7.058417e-08, 6.995661e-08], [6.834219e-08, 1.8, 6.834332e-08, 6.834356e-08], [6.834298e-08, 6.834381e-08, 1.8, 6.834406e-08], [6.833679e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655337, -0.8643391, -0.865083, -0.8653558, -0.8688432, -0.8646918, 0.8638265, -0.8659983, -0.8686779, 0.8644044, -0.8665799, -0.8652482, -0.8687515, 0.8659929, 0.8658019, -0.8666893, -0.867672, 0.8654925, 0.866874, 0.8657776]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
