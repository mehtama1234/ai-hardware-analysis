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
- cycle DAC values V: `[1.343221, 0.7353726, 0.6217281, 0.8016451]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.138892e-08, 7.027953e-08, 6.971364e-08], [6.834143e-08, 1.8, 6.834325e-08, 6.834352e-08], [6.834299e-08, 6.834382e-08, 1.8, 6.834407e-08], [6.833688e-08, 6.834149e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655363, -0.8643302, -0.8650831, -0.8653357, -0.8688455, -0.8646207, 0.8638423, -0.8659568, -0.8686792, 0.864449, -0.8665369, -0.8650969, -0.8687537, 0.8659779, 0.8658383, -0.8665643, -0.8676772, 0.8654496, 0.8668694, 0.8659021]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
