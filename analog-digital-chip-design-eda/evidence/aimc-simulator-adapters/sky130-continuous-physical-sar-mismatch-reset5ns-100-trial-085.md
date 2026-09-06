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
- cycle DAC values V: `[1.33839, 0.7390751, 0.6207754, 0.803523]`
- cycle DAC legal range: `True`
- gate legal range: `True`
- bottom-plate legal range: `True`
- bottom-plate debug values V: `[[1.8, 7.153752e-08, 7.034047e-08, 6.978891e-08], [6.834193e-08, 1.8, 6.83433e-08, 6.834354e-08], [6.834303e-08, 6.834383e-08, 1.8, 6.834407e-08], [6.833685e-08, 6.83415e-08, 1.8, 1.8]]`
- comparator differences V: `[-0.8655312, -0.8643441, -0.8650809, -0.8653549, -0.8688396, -0.8647111, 0.8638639, -0.865982, -0.8686751, 0.8644003, -0.866575, -0.8652651, -0.8687437, 0.8659924, 0.8658115, -0.8666794, -0.8676094, 0.8654874, 0.8668727, 0.8657962]`

This is a measured one-transient closed-loop physical SAR candidate. It records four physical decisions across each requested conversion; banked, clamped, and precharged candidates remain separate from acceptance until all conversion, legality, robustness, and layout gates pass.

## Refused Claim
one continuous five-conversion physical DAC/comparator transient with decision-dependent bottom controls; not PVT, mismatch/noise, extracted-layout, board, or silicon acceptance
