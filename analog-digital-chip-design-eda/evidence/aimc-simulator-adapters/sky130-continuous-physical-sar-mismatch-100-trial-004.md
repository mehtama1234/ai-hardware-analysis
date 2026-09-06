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
- cycle DAC values V: `[1.337099, 0.7420291, 0.6255373, 0.8087237]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.135742e-08, 7.02335e-08, 6.970169e-08], [6.834173e-08, 1.8, 6.834325e-08, 6.834352e-08], [6.834287e-08, 6.834376e-08, 1.8, 6.834404e-08], [6.833663e-08, 6.834139e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.865533, -0.8643625, -0.865094, -0.865396, -0.8688405, -0.8648109, 0.8637272, -0.8660285, -0.8686673, 0.8643523, -0.8666207, -0.8652856, -0.8687314, 0.8659938, 0.8658157, -0.8666334, -0.8674687, 0.8654548, 0.8668693, 0.8659549]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
