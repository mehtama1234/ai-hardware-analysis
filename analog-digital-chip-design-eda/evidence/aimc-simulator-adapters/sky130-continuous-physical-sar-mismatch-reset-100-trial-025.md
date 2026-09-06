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
- cycle DAC values V: `[1.342616, 0.7379706, 0.6206639, 0.8022828]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.16724e-08, 7.042848e-08, 6.984737e-08], [6.834192e-08, 1.8, 6.83433e-08, 6.834355e-08], [6.834303e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833693e-08, 6.834155e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655387, -0.8643413, -0.865084, -0.8653512, -0.8688407, -0.8646911, 0.8638717, -0.865965, -0.8686721, 0.8644013, -0.8665554, -0.8652205, -0.8687547, 0.8659948, 0.8658155, -0.8666309, -0.8676808, 0.8654855, 0.8668808, 0.8658392]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
