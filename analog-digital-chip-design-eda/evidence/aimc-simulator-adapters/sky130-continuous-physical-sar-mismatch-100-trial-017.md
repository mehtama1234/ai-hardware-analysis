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
- cycle DAC values V: `[1.337147, 0.7451959, 0.6224107, 0.806012]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.141033e-08, 7.021947e-08, 6.971456e-08], [6.834226e-08, 1.8, 6.834331e-08, 6.834355e-08], [6.834298e-08, 6.83438e-08, 1.8, 6.834406e-08], [6.833675e-08, 6.834141e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655338, -0.8643779, -0.8650885, -0.8653995, -0.8688406, -0.8648779, 0.8638056, -0.8659909, -0.8686677, 0.8643045, -0.8666219, -0.8653695, -0.8687317, 0.8660055, 0.8658149, -0.8666427, -0.8674727, 0.8654866, 0.8668699, 0.8659466]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
