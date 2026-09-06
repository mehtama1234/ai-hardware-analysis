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
- cycle DAC values V: `[1.339073, 0.7382401, 0.6201442, 0.8015579]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.117657e-08, 7.011489e-08, 6.961545e-08], [6.834151e-08, 1.8, 6.834325e-08, 6.834352e-08], [6.834305e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833699e-08, 6.834156e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655385, -0.8643448, -0.865084, -0.8653471, -0.8688489, -0.8646979, 0.863883, -0.8659551, -0.8686677, 0.864406, -0.8665592, -0.8652051, -0.8687415, 0.8659913, 0.865819, -0.8666187, -0.8675968, 0.8654718, 0.8668798, 0.8658606]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
