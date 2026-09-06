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
- cycle DAC values V: `[1.349486, 0.7312964, 0.619872, 0.8013849]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.144754e-08, 7.032444e-08, 6.977535e-08], [6.834125e-08, 1.8, 6.834326e-08, 6.834352e-08], [6.834305e-08, 6.834385e-08, 1.8, 6.834407e-08], [6.833692e-08, 6.834162e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655419, -0.8643137, -0.8650798, -0.8653515, -0.8688514, -0.8645168, 0.8638873, -0.8659527, -0.8686838, 0.8644929, -0.8664484, -0.8650411, -0.8687694, 0.8659645, 0.8658941, -0.8664708, -0.8677674, 0.8654197, 0.8668629, 0.8659678]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
