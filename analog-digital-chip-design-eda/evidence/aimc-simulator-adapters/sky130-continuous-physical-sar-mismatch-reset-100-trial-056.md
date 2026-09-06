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
- cycle DAC values V: `[1.335827, 0.7411672, 0.6207727, 0.8052797]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.16611e-08, 7.04018e-08, 6.985212e-08], [6.834224e-08, 1.8, 6.834332e-08, 6.834355e-08], [6.834304e-08, 6.834382e-08, 1.8, 6.834407e-08], [6.833674e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655375, -0.864354, -0.865084, -0.8653714, -0.8688458, -0.8647627, 0.8638681, -0.8660056, -0.8686651, 0.86436, -0.8666028, -0.865362, -0.8687357, 0.8660055, 0.8657807, -0.8667548, -0.867574, 0.8655121, 0.8668837, 0.8657158]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
