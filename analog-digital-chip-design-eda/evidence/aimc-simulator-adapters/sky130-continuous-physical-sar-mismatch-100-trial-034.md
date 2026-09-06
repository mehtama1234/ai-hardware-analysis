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
- cycle DAC values V: `[1.338928, 0.73969, 0.6255244, 0.8088316]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.126785e-08, 7.019116e-08, 6.967202e-08], [6.834142e-08, 1.8, 6.834323e-08, 6.83435e-08], [6.834287e-08, 6.834376e-08, 1.8, 6.834404e-08], [6.833661e-08, 6.834141e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655343, -0.8643534, -0.8650943, -0.8653968, -0.8688421, -0.8647603, 0.8637286, -0.8660298, -0.8686689, 0.8643852, -0.866588, -0.8652311, -0.8687359, 0.8659847, 0.8658409, -0.8665852, -0.8674935, 0.8654305, 0.8668661, 0.8659935]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
