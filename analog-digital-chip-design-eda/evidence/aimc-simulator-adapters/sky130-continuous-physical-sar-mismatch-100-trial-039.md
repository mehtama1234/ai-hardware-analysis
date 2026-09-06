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
- cycle DAC values V: `[1.341624, 0.7336584, 0.6257124, 0.8094826]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.0898e-08, 6.999209e-08, 6.952788e-08], [6.834071e-08, 1.8, 6.834317e-08, 6.834346e-08], [6.834286e-08, 6.834377e-08, 1.8, 6.834403e-08], [6.833653e-08, 6.834143e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655368, -0.8643312, -0.8650956, -0.8653983, -0.8688442, -0.8646207, 0.8637262, -0.8660382, -0.868671, 0.8644661, -0.8665076, -0.8650765, -0.8687409, 0.8659582, 0.8659011, -0.8664604, -0.8675127, 0.8653606, 0.8668565, 0.8660845]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
